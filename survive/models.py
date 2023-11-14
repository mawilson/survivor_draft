from django.db import models

# Create your models here.

class Team(models.Model):
    name = models.CharField(max_length = 300)
    captain = models.CharField(max_length = 300)

    def __str__(self) -> str:
        """Returns a string representation of a Survivor Team"""
        return f"Team name: {self.name}. Captain: '{self.captain}'"
    
    def points(self) -> int:
        total = 0
        for s in Survivor.objects.filter(team=self):
            total += s.points()[0]
        return total

class Rubric(models.Model):
    idols = models.IntegerField(default=2, null=False)
    immunities = models.IntegerField(default=2, null=False)
    jury_number = models.IntegerField(default=1, null=False)
    fan_favorite = models.IntegerField(default=2, null=False)
    finalist = models.IntegerField(default=2, null=False)
    winner = models.IntegerField(default=5, null=False)

    def __str__(self) -> str:
        """Returns a string representation of the scoring rubric."""
        return f"Most idols: {self.idols} pts; Number on jury: {self.jury_number} pts; Fan favorite: {self.fan_favorite} pts; Winner: {self.winner} pts."
class Survivor(models.Model):
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
        """Returns a two-element tuple, first element is total points earned by this Survivor, second element is a string describing that math."""
        rubric = Rubric.objects.first() # should define a default rubric for None
        total = 0
        description = "POINTS BREAKDOWN\nPoints Earned * Rubric Value = Score\n"
        total += self.idols * rubric.idols
        description += f"Most idol points: {self.idols} * {rubric.idols} = {self.idols * rubric.idols}\n"
        total += self.immunities * rubric.immunities
        description += f"Most individual immunities: {self.immunities} * {rubric.immunities} = {self.immunities * rubric.immunities}\n"
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
    
