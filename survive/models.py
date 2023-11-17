from django.db import models
import functools
import math

# Create your models here.

class Season(models.Model):
    """Basically just a container for everything Survivor, per season"""
    name = models.CharField(max_length=300)

    def most_idols(self):
        """Returns the list of Survivors with the most idols in this season"""
        idol_survivors = []
        for s in self.survivor_set.all():
            if len(idol_survivors) == 0 or s.idols > idol_survivors[0].idols:
                idol_survivors = [s]
            elif s.idols == idol_survivors[0].idols:
                idol_survivors.append(s)

        idol_survivors_winningest_teams = [] # initial tiebreaker on most idol ties is whose team had the most cumulative idols, filter out survivors with lesser teams here
        most_team_idols = 0
        s_team_idols = 0
        for s in idol_survivors:
            s_team_idols = s.team.idols() # store in a variable so we don't get from DB repeatedly
            if s_team_idols > most_team_idols:
                idol_survivors_winningest_teams = [s]
                most_team_idols = s_team_idols
            elif s_team_idols == most_team_idols:
                idol_survivors_winningest_teams.append(s)

        return idol_survivors_winningest_teams
    
    def most_immunities(self):
        """Returns the Survivors with the most immunities in the season"""
        imm_survivors = []
        for s in self.survivor_set.all():
            if len(imm_survivors) == 0 or s.immunities > imm_survivors[0].immunities:
                imm_survivors = [s]
            elif s.immunities == imm_survivors[0].immunities:
                imm_survivors.append(s)

        imm_survivors_winningest_teams = [] # initial tiebreaker on most immunity ties is whose team had the most immunities, filter out survivors with lesser teams here
        most_imms = 0
        s_team_imms = 0
        for s in imm_survivors:
            s_team_imms = s.team.immunities() # store in a variable so we don't get from DB repeatedly
            if s_team_imms > most_imms:
                imm_survivors_winningest_teams = [s]
                most_imms = s_team_imms
            elif s_team_imms == most_imms:
                imm_survivors_winningest_teams.append(s)
        
        return imm_survivors_winningest_teams

class Team(models.Model):
    season = models.ForeignKey(
        Season,
        on_delete = models.CASCADE, # If a Season goes, so too goes every Team within it
        verbose_name="the season a team belongs to",
        null = True
    )
    name = models.CharField(max_length = 300)
    captain = models.CharField(max_length = 300)

    def __str__(self) -> str:
        """Returns a string representation of a Survivor Team"""
        return f"Team name: {self.name}. Captain: '{self.captain}'"
    
    def points(self) -> int:
        """Returns the sum of all points earned by Survivors within this team"""
        total = 0
        for s in Survivor.objects.filter(team=self):
            total += s.points()[0]
        return total
    
    def idols(self) -> int:
        """Returns the sum of all idols earned by Survivors within this team"""
        total = 0
        for s in Survivor.objects.filter(team=self):
            total += s.idols
        return total

    def immunities(self) -> int:
        """Returns the sum of all individual immunities won by Survivors within this team"""
        #return functools.reduce(lambda a, b: a.immunities + b.immunities, self.survivor_set.all())
        total = 0
        for s in self.survivor_set.all():
            total += s.immunities
        return total

class Rubric(models.Model):
    season = models.ForeignKey(
        Season,
        on_delete = models.CASCADE, # If a Season goes, so too goes every Team within it
        verbose_name="the season a team belongs to",
        null = True
    )

    # following two parameters have to do with scoring for the most idols & whether to split points on ties
    idols = models.IntegerField(default=2, null=False)
    idols_tie_split = models.BooleanField(default=True, null=False)

    # following two parameters have to do with scoring for the most individual immunities & whether to split points on ties
    immunities = models.IntegerField(default=2, null=False)
    immunities_tie_split = models.BooleanField(default=True, null=False)

    jury_number = models.IntegerField(default=1, null=False)
    fan_favorite = models.IntegerField(default=2, null=False)
    finalist = models.IntegerField(default=2, null=False)
    winner = models.IntegerField(default=5, null=False)

    def __str__(self) -> str:
        """Returns a string representation of the scoring rubric."""
        return f"Most idols: {self.idols} pts; Number on jury: {self.jury_number} pts; Fan favorite: {self.fan_favorite} pts; Winner: {self.winner} pts."
class Survivor(models.Model):
    season = models.ForeignKey(
        Season,
        on_delete = models.CASCADE, # If a Season goes, so too goes every Team within it
        verbose_name="the season a team belongs to",
        null = True
    )
    name = models.CharField(max_length=100)
    status = models.BooleanField(default=False, null=False, verbose_name="Elimination Status")
    team = models.ForeignKey(
        Team,
        on_delete = models.CASCADE, # if a Survivor's Team gets deleted, so too does that Survivor
        verbose_name = "the team that recruited this survivor",
        null = True # nothing wrong with a Survivor having no Team, theoretically
    )
    idols = models.IntegerField(default=0, null=False)
    advantages = models.IntegerField(default=0, null=False)
    immunities = models.IntegerField(default=0, null=False)
    jury_number = models.IntegerField(default=0, null=False)
    confessionals = models.IntegerField(default=0, null=False)
    fan_favorite = models.BooleanField(default=False, null=False)
    finalist = models.BooleanField(default=False, null=False) # Winner is an upgraded finalist
    winner = models.BooleanField(default=False, null=False)

    def __str__(self) -> str:
        """Returns a string representation of a Survivor contestant"""
        _status = "Surviving" if self.status else "Eliminated" 
        return f"Contestant name: {self.name}. Team: {self.team}. Status: {_status}"
    
    def points(self) -> (int, str): # turn into a tuple - first the integer, second the descriptor string?
        """Returns a two-element tuple, first element is total points earned by this Survivor, second element is a string describing that math"""
        rubric = Rubric.objects.first() # should define a default rubric for None
        total = 0
        description = "POINTS BREAKDOWN\nPoints Earned * Rubric Value = Score\n"
        
        most_idol_winners = self.season.most_idols()
        most_idols = self in most_idol_winners # if self is one of the Survivors with the most idols
        if most_idols:
            if len(most_idol_winners) > 1 and rubric.idols_tie_split: # if there is a tie for most idol winners and the rubric says to split ties
                total += math.ceil(rubric.idols / len(most_idol_winners))
                description += f"Most idol points (tie): Ceiling({rubric.idols} / {len(most_idol_winners)}) = {math.ceil(rubric.idols / len(most_idol_winners))}\n"
            else: # else just give full rubric idols points
                total += rubric.idols
                description += f"Most idol points: {rubric.idols} = {rubric.idols}\n"

        most_immunities_winners = self.season.most_immunities()
        most_immunities = self in most_immunities_winners # if self is one of the Survivors with the most immunities
        if most_immunities:
            if len(most_immunities_winners) > 1 and rubric.immunities_tie_split: # if there is a tie for most immunities and the rubric says to split ties
                total += math.ceil(rubric.immunities / len(most_immunities_winners))
                description += f"Most immunities points (tie): Ceiling({rubric.immunities} / {len(most_immunities_winners)}) = {math.ceil(rubric.immunities / len(most_immunities_winners))}\n"
            else: # else just give full rubric immunities points
                total += rubric.immunities
                description += f"Most individual immunities: {rubric.immunities} = {rubric.immunities}\n"

        total += self.jury_number * rubric.jury_number
        description += f"Jury number: {self.jury_number} * {rubric.jury_number} = {self.jury_number * rubric.jury_number} \n"
        if self.fan_favorite:
            total += rubric.fan_favorite
            description += f"Fan favorite: {self.fan_favorite} * {rubric.fan_favorite} = {rubric.fan_favorite}\n"
        if self.finalist:
            if self.winner:
                total += self.winner * rubric.winner
                description += f"Winner: {self.winner} * {rubric.winner} = {rubric.winner}"
            else:
                total += self.finalist * rubric.finalist
                description += f"Finalist: {self.finalist} * {rubric.finalist} = {self.finalist * rubric.finalist}"
        return total, description.strip() # remove trailing newline if present
    
