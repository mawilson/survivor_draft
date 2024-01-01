from django.db import models
import math
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from datetime import date

# Create your models here.

class Rubric(models.Model):
    # following two fields have to do with scoring for the most idols & whether to split points on ties
    idols = models.IntegerField(default=2, null=False)
    idols_tie_split = models.BooleanField(default=True, null=False)

    # following two fields have to do with scoring for the most individual immunities & whether to split points on ties
    immunities = models.IntegerField(default=2, null=False)
    immunities_tie_split = models.BooleanField(default=True, null=False)

    jury_number = models.IntegerField(default=1, null=False)

    fan_favorite = models.IntegerField(default=2, null=False)
    fan_favorite_self_votes = models.BooleanField(default=False, null=False)
    fan_favorite_negative_votes = models.BooleanField(default=True, null=False)

    finalist = models.IntegerField(default=2, null=False)
    winner = models.IntegerField(default=5, null=False)

    @classmethod
    def get_default_pk(r):
        """Used to create a default Rubric if one does not exist, for use by a Season"""
        rubric, created = r.objects.get_or_create(
            defaults = dict(
                idols = 2,
                idols_tie_split = True,
                immunities = 2,
                immunities_tie_split = True,
                jury_number = 1,
                fan_favorite = 2,
                finalist = 2,
                winner = 5,
                fan_favorite_self_votes = False,
                fan_favorite_negative_votes = True,
            )
        )
        return rubric.pk

    def __str__(self) -> str:
        """Returns a string representation of the scoring rubric."""
        return f"Most idols: {self.idols} pts; Number on jury: {self.jury_number} pts; Fan favorite: {self.fan_favorite} pts; Winner: {self.winner} pts."

class Season(models.Model):
    """Basically just a container for everything Survivor, per season"""
    name = models.CharField(max_length=300)
    rubric = models.ForeignKey(
        Rubric,
        on_delete = models.SET_DEFAULT, # If a Rubric goes, adjust season rubric to the default
        null = False,
        default = Rubric.get_default_pk
    )
    season_close = models.DateField(null = True) # used to close the fan favorite & 'finalize' a season

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
    
    def jury_number(self):
        """Returns one more than the highest jury number of all eliminated Survivors"""
        highest_jury_number = 0
        winner = False
        for s in self.survivor_set.all():
            if not s.status and s.jury_number > highest_jury_number:
                highest_jury_number = s.jury_number
            if s.winner:
                winner = True # if it's over, highest jury number is just the value of the highest eliminated - don't give finalists an extra point
        return highest_jury_number if winner else highest_jury_number + 1 # for use by other Survivors, jury number is always one better than the last eliminated survivor
        # cannot return higher than max_jury_number

    def placement(self):
        """Returns one less than the lowest placement of all eliminated Survivors"""
        lowest_placement = len(self.survivor_set.all())
        for s in self.survivor_set.all():
            if not s.status and s.placement < lowest_placement:
                lowest_placement = s.placement
        return max(lowest_placement - 1, 1) # for use by other Survivors, placement is always one better than the last eliminated Survivor
        # cannot return lower than 1
    
    def fan_favorites(self, save=False):
        """Returns a two element tuple - first the list of survivors with the most fan favorite votes, with tiebreakers being most 1st or 2nd place votes,
        & second the dictionary of survivors who received votes, & what those votes were
        Also assigns the Survivor.fan_favorite Boolean attribute for each survivor in the season
        Accepts optional save parameter which, if True, saves the fan_favorite attribute on each Survivor within this season based upon the voting"""
        vote_dict = {}
        for t in self.team_set.all():
            if t.fan_favorite_first: # if the vote is defined, add it to the dictionary for that survivor
                if t.fan_favorite_first.id not in vote_dict:
                    vote_dict[t.fan_favorite_first.id] = [3] # instantiate the list with a first place vote
                else:
                    vote_dict[t.fan_favorite_first.id].append(3) # add a first place vote to the list
            if t.fan_favorite_second:
                if t.fan_favorite_second.id not in vote_dict:
                    vote_dict[t.fan_favorite_second.id] = [2] # instantiate the list with a second place vote
                else:
                    vote_dict[t.fan_favorite_second.id].append(2) # add a second place vote to the list
            if t.fan_favorite_third:
                if t.fan_favorite_third.id not in vote_dict:
                    vote_dict[t.fan_favorite_third.id] = [1] # instantiate the list with a third place vote
                else:
                    vote_dict[t.fan_favorite_third.id].append(1) # add a third place vote to the list
            if t.fan_favorite_bad:
                if t.fan_favorite_bad.id not in vote_dict:
                    vote_dict[t.fan_favorite_bad.id] = [-1] # instantiate the list with a negative vote
                else:
                    vote_dict[t.fan_favorite_bad.id].append(-1) # add a negative place vote to the list
        
        # sum the votes up & append them to the end of each dictionary entry's list
        # also append number of first, second, third, & bad votes after that
        for k, v in vote_dict.items():
            sum = 0
            num_firsts = 0
            num_seconds = 0
            num_thirds = 0
            num_bads = 0
            for vote in v:
                if vote == -1:
                    if self.rubric.fan_favorite_negative_votes: # even if present, negative votes don't count if rubric disallows them
                        sum += vote
                        num_bads += 1
                else:
                    sum += vote
                    if vote == 3:
                        num_firsts += 1
                    elif vote == 2:
                        num_seconds += 1
                    elif vote == 1:
                        num_thirds += 1
            v.append(sum) # sum at -5
            v.append(num_firsts) # num_firsts at -4
            v.append(num_seconds) # num_seconds at -3
            v.append(num_thirds) # num_thirds at -2
            v.append(num_bads) # num_bads at -1

        # iterate thru once more looking for the highest sum, then use num_firsts followed by num_seconds as tiebreaker
        # can still have multiple fan favorites
        fan_favorites = []
        favoritest_sum = 0
        favoritest_firsts = 0
        favoritest_seconds = 0
        for k, v in vote_dict.items():
            if len(fan_favorites) == 0: # if list is empty, no need for comparisons
                fan_favorites.append(k)
                # save these now for comparison later - we could look it up again but the syntax starts to look bonkers
                favoritest_sum = v[-5] # fifth last element is the sum
                favoritest_firsts = v[-4] # fourth last element is the firsts
                favoritest_seconds = v[-3] # third last element is the seconds
            elif v[-5] > favoritest_sum: # if this survivor is more favorited, replace the existing favorites list
                fan_favorites = [k]
                favoritest_sum = v[-5]
                favoritest_firsts = v[-4]
                favoritest_seconds = v[-3]
            elif v[-5] == favoritest_sum: # this survivor is as favorited, check for tiebreaks
                if v[-4] > favoritest_firsts:
                    fan_favorites = [k]
                    favoritest_sum = v[-5]
                    favoritest_firsts = v[-4]
                    favoritest_seconds = v[-3]
                elif v[-4] == favoritest_firsts:
                    if v[-3] > favoritest_seconds:
                        fan_favorites = [k]
                        favoritest_sum = v[-5]
                        favoritest_firsts = v[-4]
                        favoritest_seconds = v[-3]
                    elif v[-3] == favoritest_seconds:
                        fan_favorites.append(k)
    
        favorite_survivors = self.survivor_set.filter(id__in=fan_favorites)
        if save:
            for s in self.survivor_set.all():
                s.fan_favorite = s in favorite_survivors
                s.save()

        for key, value in vote_dict.items(): # add survivor names to the dict for display purposes by fan_favorite_vote results
            value.append(self.survivor_set.filter(id=key)[0].name)

        return (favorite_survivors, vote_dict) # return only the survivors whose ID is in the fan_favorites list
    
    def fan_favorites_display(self):
        """"Helper function for displaying the results of the fan_favorites function. Returns a list of formatted strings describing the votes each survivor received."""
        description = ["Points totals:"]
        vote_dict = self.fan_favorites()[1]
        vote_dict_sorted_by_sum = sorted(vote_dict.items(), key=lambda item: item[1][-6], reverse = True) # sorts vote_dict.items by their values (1) & then the sixth-last item in that value (sum)
        # after appending name to end of list, sum is at -6, firsts at -5, seconds at -4, thirds at -3, bads at -2, & name at -1
        for key, value in vote_dict_sorted_by_sum:
            if self.rubric.fan_favorite_negative_votes:
                if value[-6] == 1:
                    description.append(f"{value[-1]}: {value[-6]} point ({value[-5]} 1st, {value[-4]} 2nd, {value[-3]} 3rd, {value[-2]} bad votes)")
                else:
                    description.append(f"{value[-1]}: {value[-6]} points ({value[-5]} 1st, {value[-4]} 2nd, {value[-3]} 3rd, {value[-2]} bad votes)")
            else:
                if value[-6] == 1:
                    description.append(f"{value[-1]}: {value[-6]} point ({value[-5]} 1st, {value[-4]} 2nd, {value[-3]} 3rd votes)")
                else:
                    description.append(f"{value[-1]}: {value[-6]} points ({value[-5]} 1st, {value[-4]} 2nd, {value[-3]} 3rd votes)")
        return description

    def fan_favorites_no_vote(self):
        """Returns a string representation of survivors whose fan_favorite attribute is True"""
        favorites = self.survivor_set.filter(fan_favorite=True)
        if len(favorites) > 1:
            return ", ".join(favorites)
        elif len(favorites) == 0:
            return "nobody"
        else:
            return favorites.first()

    def is_season_open(self):
        """Returns True if today's date is on or before the season closing date (or closing date is null), else False."""
        return self.season_close is None or (date.today() < self.season_close)

class Team(models.Model):
    season = models.ForeignKey(
        Season,
        on_delete = models.CASCADE, # If a Season goes, so too goes every Team within it
        verbose_name = "the season a team belongs to",
        null = True
    )
    name = models.CharField(max_length = 300)
    captain = models.CharField(max_length = 300)
    winner = models.BooleanField(default=False, null=False)
    
    fan_favorite_first = models.ForeignKey(
        "Survivor", # trick the compiler into letting us reference a class not yet defined
        on_delete = models.SET_NULL,
        verbose_name = "First place fan favorite vote submitted by this team",
        null = True, # a team can forgo a vote
        related_name = "+", # no need for backwards relating a fan fave survivor to the team that voted it
        blank = True
    )
    fan_favorite_second = models.ForeignKey(
        "Survivor", # trick the compiler into letting us reference a class not yet defined
        on_delete = models.SET_NULL,
        verbose_name = "Second place fan favorite vote submitted by this team",
        null = True, # a team can forgo a vote
        related_name = "+", # no need for backwards relating a fan fave survivor to the team that voted it
        blank = True
    )
    fan_favorite_third = models.ForeignKey(
        "Survivor", # trick the compiler into letting us reference a class not yet defined
        on_delete = models.SET_NULL,
        verbose_name = "Third place fan favorite vote submitted by this team",
        null = True, # a team can forgo a vote
        related_name = "+", # no need for backwards relating a fan fave survivor to the team that voted it
        blank = True
    )
    fan_favorite_bad = models.ForeignKey(
        "Survivor", # trick the compiler into letting us reference a class not yet defined
        on_delete = models.SET_NULL,
        verbose_name = "Negative place fan favorite vote submitted by this team",
        null = True, # a team can forgo a vote
        related_name = "+", # no need for backwards relating a fan fave survivor to the team that voted it
        blank = True
    )

    def clean(self):
        errors = []

        if self.season is not None:
            if self.fan_favorite_first is not None and self.fan_favorite_first == self.fan_favorite_second:
                errors.append(ValidationError(_("First and second vote cannot be the same"), code="matched12"))
            if self.fan_favorite_first is not None and self.fan_favorite_first == self.fan_favorite_third:
                errors.append(ValidationError(_("First and third vote cannot be the same"), code="matched13"))
            if self.fan_favorite_first is not None and self.fan_favorite_first == self.fan_favorite_bad:
                errors.append(ValidationError(_("First and bad vote cannot be the same"), code="matched14"))
            if self.fan_favorite_second is not None and self.fan_favorite_second == self.fan_favorite_third:
                errors.append(ValidationError(_("Second and third vote cannot be the same"), code="matched23"))
            if self.fan_favorite_second is not None and self.fan_favorite_second == self.fan_favorite_bad:
                errors.append(ValidationError(_("Second and bad vote cannot be the same"), code="matched24"))
            if self.fan_favorite_third is not None and self.fan_favorite_third == self.fan_favorite_bad:
                errors.append(ValidationError(_("Third and bad vote cannot be the same"), code="matched34"))
            
            if not self.season.rubric.fan_favorite_self_votes: # if self votes are disallowed, validate them
                if self.fan_favorite_first is not None and self.fan_favorite_first.team == self:
                    errors.append(ValidationError(_("First vote cannot be for a player on your own team"), code="sameTeam1"))
                if self.fan_favorite_second is not None and self.fan_favorite_second.team == self:
                    errors.append(ValidationError(_("Second vote cannot be for a player on your own team"), code="sameTeam2"))
                if self.fan_favorite_third is not None and self.fan_favorite_third.team == self:
                    errors.append(ValidationError(_("Third vote cannot be for a player on your own team"), code="sameTeam3"))
                if self.fan_favorite_bad is not None and self.fan_favorite_bad.team == self:
                    errors.append(ValidationError(_("Bad vote cannot be for a player on your own team"), code="sameTeam4"))

        if len(errors) > 0:
            raise ValidationError(errors)

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
        total = 0
        for s in self.survivor_set.all():
            total += s.immunities
        return total
    
    def lost(self) -> bool:
        """If season is over, returns True if this team won, else False"""
        """Returns True if all survivors on this team have been eliminated, & this team's points total (plus fan favorite value) is lower than some other team's"""
        if not self.season.is_season_open():
            return not self.winner
        elif all(not s.status for s in self.survivor_set.all()):
            my_theoretical_points = self.points() + self.season.rubric.fan_favorite # fan favorite points are the only thing we could theoretically still earn
            for t in self.season.team_set.all():
                if t is self:
                    continue
                elif t.points() > my_theoretical_points: # if any other team has more points than myself, & all my survivors are out, I have officially lost, return True
                    return True
        return False

class Survivor(models.Model):
    season = models.ForeignKey(
        Season,
        on_delete = models.CASCADE, # If a Season goes, so too goes every Team within it
        verbose_name="the season a team belongs to",
        null = True
    )
    name = models.CharField(max_length=100)
    status = models.BooleanField(default=False, null=False, verbose_name="Elimination Status - False for eliminated, True for surviving")
    team = models.ForeignKey(
        Team,
        on_delete = models.CASCADE, # if a Survivor's Team gets deleted, so too does that Survivor
        verbose_name = "the team that recruited this survivor",
        null = True # nothing wrong with a Survivor having no Team, theoretically
    )
    tribe = models.CharField(max_length=10, null=True) # Usually 'Red', 'Yellow', or 'Blue', but no tribe or some other value are valid
    idols = models.IntegerField(default=0, null=False)
    advantages = models.IntegerField(default=0, null=False)
    immunities = models.IntegerField(default=0, null=False)
    jury_number = models.IntegerField(default=0, null=False)
    placement = models.IntegerField(default = 0, null=False) # place eliminated, where 0 is not yet eliminated, 1 is first, high number is last
    confessionals = models.IntegerField(default=0, null=False)
    fan_favorite = models.BooleanField(default=False, null=False) # this is calculated, but we don't want to run the calqs every time, so still saving it when Season.fan_favorites() runs
    finalist = models.BooleanField(default=False, null=False) # Winner is an upgraded finalist
    winner = models.BooleanField(default=False, null=False)
    pic = models.ImageField(default=False, null=True) # a null image will use a default blank image
    pic_full = models.ImageField(default=False, null=True) # larger image used by Survivor page, can also be null

    def __str__(self) -> str:
        """Returns a string representation of a Survivor contestant"""
        _status = "Surviving" if self.status else "Eliminated" 
        #return f"Contestant name: {self.name}. Team: {self.team}. Status: {_status}"
        return self.name

    def points(self) -> (int, str): # turn into a tuple - first the integer, second the descriptor string?
        """Returns a two-element tuple, first element is total points earned by this Survivor, second element is a string describing that math"""
        rubric = self.season.rubric
        total = 0
        description = "POINTS BREAKDOWN\nPoints Earned * Rubric Value = Score\n"
        
        if self.idols > 0: # cannot award idol points if at least one idol hasn't been earned
            most_idol_winners = self.season.most_idols()
            most_idols = self in most_idol_winners # if self is one of the Survivors with the most idols
            if most_idols:
                if len(most_idol_winners) > 1 and rubric.idols_tie_split: # if there is a tie for most idol winners and the rubric says to split ties
                    total += math.ceil(rubric.idols / len(most_idol_winners))
                    description += f"Most idol points (tie): Ceiling({rubric.idols} / {len(most_idol_winners)}) = {math.ceil(rubric.idols / len(most_idol_winners))}\n"
                else: # else just give full rubric idols points
                    total += rubric.idols
                    description += f"Most idol points: {rubric.idols} = {rubric.idols}\n"

        if self.immunities > 0: # cannot award immunity points if at least one immunity hasn't been earned
            most_immunities_winners = self.season.most_immunities()
            most_immunities = self in most_immunities_winners # if self is one of the Survivors with the most immunities
            if most_immunities:
                if len(most_immunities_winners) > 1 and rubric.immunities_tie_split: # if there is a tie for most immunities and the rubric says to split ties
                    total += math.ceil(rubric.immunities / len(most_immunities_winners))
                    description += f"Most immunities points (tie): Ceiling({rubric.immunities} / {len(most_immunities_winners)}) = {math.ceil(rubric.immunities / len(most_immunities_winners))}\n"
                else: # else just give full rubric immunities points
                    total += rubric.immunities
                    description += f"Most individual immunities: {rubric.immunities} = {rubric.immunities}\n"

        if self.status: # if alive, jury points are dictated by highest-scoring eliminated survivor
            jury_points = self.season.jury_number()
            total += jury_points * rubric.jury_number
            description += f"Jury number: {jury_points} * {rubric.jury_number} = {jury_points * rubric.jury_number}\n"
        else: # if eliminated, jury points are only dictated by own entry
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