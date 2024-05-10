from django.db import models
import math
import random
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from datetime import date
from django.contrib.auth.models import User

# Create your models here.


class Rubric(models.Model):
    name = models.CharField(
        blank=False,
        null=False,
        default="Rubric",
        verbose_name="A name to identify this rubric by.",
        max_length=100
    )
    # following two fields have to do with scoring for the most idols & whether to split points on ties
    idols = models.IntegerField(
        default=2,
        null=False,
        verbose_name="The points awarded to the survivor with the most immunity idols. Does not include other miscellaneous advantages.",
    )
    idols_tie_split = models.BooleanField(
        default=True,
        null=False,
        verbose_name="Whether ties in most idols split points. True means points are split, False means each survivor is rewarded the maximum value.",
    )

    # following two fields have to do with scoring for the most individual immunities & whether to split points on ties
    immunities = models.IntegerField(
        default=2,
        null=False,
        verbose_name="The points awarded to the survivor who won the most immunity challenges.",
    )
    immunities_tie_split = models.BooleanField(
        default=True,
        null=False,
        verbose_name="Whether ties in most immunities split points. True means points are split, False means each survivor is rewarded the maximum value.",
    )

    confessionals = models.IntegerField(
        default=2,
        null=False,
        verbose_name="The points awarded to the survivor who featured in the most confessionals.",
    )
    confessionals_tie_split = models.BooleanField(
        default=True,
        null=False,
        verbose_name="Whether ties in most confessionals split points. True means points are split, False means each survivor is rewarded the maximum value.",
    )

    jury_number = models.IntegerField(
        default=1,
        null=False,
        verbose_name="The points awarded based on when a survivor reached the jury. Survivors never eliminated will receive the highest jury number awarded in the season. \
        The first survivor to be a member of the jury receives this many points, & subsequent survivors receive a multiple of that.",
    )
    pity_point = models.IntegerField(
        default=0,
        null=False,
        verbose_name="Points awarded to the first eliminated survivor.",
    )

    fan_favorite = models.IntegerField(
        default=2,
        null=False,
        verbose_name="The points awarded to the fan favorite, optionally determined by a vote on this site.",
    )
    fan_favorite_self_votes = models.BooleanField(
        default=False,
        null=False,
        verbose_name="Whether the fan favorite vote allows you to vote for survivors on your own team. True means you can self-vote, False means you cannot.",
    )
    fan_favorite_negative_votes = models.BooleanField(
        default=True,
        null=False,
        verbose_name="Whether the fan favorite vote includes a 'bad' vote. True means the bad vote is present, False means it is not.",
    )
    fan_favorite_share_votes = models.BooleanField(
        default=True,
        null=False,
        verbose_name="Whether fan favorite vote for this season includes all linked seasons' votes, or just its own. True includes linked season votes, False does not.",
    )

    finalist = models.IntegerField(
        default=2,
        null=False,
        verbose_name="The points awarded to the survivors who make it to the final jury, but don't win. The winner does not receive these points.",
    )
    winner = models.IntegerField(
        default=5,
        null=False,
        verbose_name="The points awarded to the sole survivor of the season. This is awarded instead of Finalist points, not in addition to.",
    )

    def __str__(self) -> str:
        """Returns a string representation of the scoring rubric."""
        return f"Name: {self.name}; Most idols: {self.idols}; Number on jury: {self.jury_number}; Fan favorite: {self.fan_favorite}; Winner: {self.winner}..."


class Season(models.Model):
    """Basically just a container for everything Survivor, per season"""

    name = models.CharField(max_length=300)
    rubric = models.ForeignKey(
        Rubric,
        on_delete=models.SET_NULL,  # If a Rubric goes, adjust season rubric to the default
        null=True,
    )
    season_close = models.DateField(
        null=True, verbose_name="Season Close", blank=True, default=None
    )  # used to close the fan favorite & 'finalize' a season
    season_open = models.DateField(
        null=True, verbose_name="Season Open", blank=True, default=None
    )  # used to close the predictions
    survivor_drafting = models.BooleanField(
        default=False, null=False, verbose_name="Survivor Drafting"
    )  # used to allow drafting of survivors
    team_creation = models.BooleanField(
        default=True, null=False, verbose_name="Team Creation"
    )  # used to allow creation of teams
    linked_seasons = models.ManyToManyField(  # type: ignore[var-annotated]
        "Season",  # trick the compiler into letting us reference a class not yet defined
        verbose_name="The other seasons this season is associated with",
        blank=True,
        default=None,
        symmetrical=True,  # if one season is related to another, another is related to one
    )
    draft_marker = models.IntegerField(
        default=1,
        verbose_name="Number representing the spot in the draft, with 1 being the first draft & going up from there",
    )
    managed_season = models.BooleanField(
        default=True,
        null=False,
        verbose_name="Managed Season: true if season is managed by a draft owner Team",
    )

    def __str__(self) -> str:
        """Returns a string representation of a Season"""
        return f"Season name: {self.name}."

    def most_idols(self):
        """Returns the list of Survivors with the most idols in this season"""
        idol_survivors = []
        for s in self.survivor_set.all():
            if len(idol_survivors) == 0 or s.idols > idol_survivors[0].idols:
                idol_survivors = [s]
            elif s.idols == idol_survivors[0].idols:
                idol_survivors.append(s)

        idol_survivors_winningest_teams = (
            []
        )  # initial tiebreaker on most idol ties is whose team had the most cumulative idols, filter out survivors with lesser teams here
        most_team_idols = 0
        s_team_idols = 0
        for s in idol_survivors:
            team = s.team.filter(
                season_id=self.id
            ).first()  # get first matching team for this survivor that competed in this season
            if team:
                s_team_idols = (
                    team.idols()
                )  # store in a variable so we don't get from DB repeatedly
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

        imm_survivors_winningest_teams = (
            []
        )  # initial tiebreaker on most immunity ties is whose team had the most immunities, filter out survivors with lesser teams here
        most_imms = 0
        s_team_imms = 0
        for s in imm_survivors:
            team = s.team.filter(
                season_id=self.id
            ).first()  # get first matching team for this survivor that competed in this season
            if team:
                s_team_imms = (
                    team.immunities()
                )  # store in a variable so we don't get from DB repeatedly
                if s_team_imms > most_imms:
                    imm_survivors_winningest_teams = [s]
                    most_imms = s_team_imms
                elif s_team_imms == most_imms:
                    imm_survivors_winningest_teams.append(s)

        return imm_survivors_winningest_teams

    def most_confessionals(self):
        """Returns the Survivors with the most confessionals in the season"""
        conf_survivors = []
        for s in self.survivor_set.all():
            if (
                len(conf_survivors) == 0
                or s.confessionals > conf_survivors[0].confessionals
            ):
                conf_survivors = [s]
            elif s.confessionals == conf_survivors[0].confessionals:
                conf_survivors.append(s)

        conf_survivors_winningest_teams = (
            []
        )  # initial tiebreaker on most confessional ties is whose team had the most confessionals, filter out survivors with lesser teams here
        most_confs = 0
        s_team_confs = 0
        for s in conf_survivors:
            team = s.team.filter(
                season_id=self.id
            ).first()  # get first matching team for this survivor that competed in this season
            if team:
                s_team_confs = (
                    team.confessionals()
                )  # store in a variable so we don't get from DB repeatedly
                if s_team_confs > most_confs:
                    conf_survivors_winningest_teams = [s]
                    most_confs = s_team_confs
                elif s_team_confs == most_confs:
                    conf_survivors_winningest_teams.append(s)

        return conf_survivors_winningest_teams

    def jury_number(self):
        """Returns one more than the highest jury number of all eliminated Survivors. 0 if no Survivors eliminated yet."""
        highest_jury_number = 0
        winner = False
        fresh_season = True  # until a Survivor has been eliminated with a non-zero jury number, we don't begin incrementing the jury number
        for s in self.survivor_set.all():
            if fresh_season and not s.status and s.jury_number > 0:
                fresh_season = False
            if not s.status and s.jury_number > highest_jury_number:
                highest_jury_number = s.jury_number
            if s.winner:
                winner = True  # if it's over, highest jury number is just the value of the highest eliminated - don't give finalists an extra point
        if fresh_season:
            return 0
        elif winner:
            return highest_jury_number
        else:
            return (
                highest_jury_number + 1
            )  # for use by other Survivors, jury number is always one better than the last eliminated survivor

    def placement(self):
        """Returns one less than the lowest placement of all eliminated Survivors"""
        lowest_placement = len(self.survivor_set.all())
        for s in self.survivor_set.all():
            if not s.status and s.placement < lowest_placement:
                lowest_placement = s.placement
        return max(
            lowest_placement - 1, 1
        )  # for use by other Survivors, placement is always one better than the last eliminated Survivor
        # cannot return lower than 1

    def fan_favorites(self, save=False):
        """Returns a two element tuple - first the list of survivors with the most fan favorite votes, with tiebreakers being most 1st or 2nd place votes,
        & second the dictionary of survivors who received votes, & what those votes were
        Accepts optional save parameter which, if True, saves the fan_favorite attribute on each Survivor within this season based upon the voting
        """
        vote_dict = {}
        voting_teams = self.team_set.all()
        if (
            self.rubric.fan_favorite_share_votes
        ):  # if shared votes are enabled, include teams from linked seasons as well
            for season in self.linked_seasons.all():
                voting_teams = voting_teams | season.team_set.all()

        for t in voting_teams:
            if (
                t.fan_favorite_first
            ):  # if the vote is defined, add it to the dictionary for that survivor
                if t.fan_favorite_first.id not in vote_dict:
                    vote_dict[t.fan_favorite_first.id] = [
                        3
                    ]  # instantiate the list with a first place vote
                else:
                    vote_dict[t.fan_favorite_first.id].append(
                        3
                    )  # add a first place vote to the list
            if t.fan_favorite_second:
                if t.fan_favorite_second.id not in vote_dict:
                    vote_dict[t.fan_favorite_second.id] = [
                        2
                    ]  # instantiate the list with a second place vote
                else:
                    vote_dict[t.fan_favorite_second.id].append(
                        2
                    )  # add a second place vote to the list
            if t.fan_favorite_third:
                if t.fan_favorite_third.id not in vote_dict:
                    vote_dict[t.fan_favorite_third.id] = [
                        1
                    ]  # instantiate the list with a third place vote
                else:
                    vote_dict[t.fan_favorite_third.id].append(
                        1
                    )  # add a third place vote to the list
            if t.fan_favorite_bad:
                if t.fan_favorite_bad.id not in vote_dict:
                    vote_dict[t.fan_favorite_bad.id] = [
                        -1
                    ]  # instantiate the list with a negative vote
                else:
                    vote_dict[t.fan_favorite_bad.id].append(
                        -1
                    )  # add a negative place vote to the list

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
                    if (
                        self.rubric.fan_favorite_negative_votes
                    ):  # even if present, negative votes don't count if rubric disallows them
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
            v.append(sum)  # sum at -5
            v.append(num_firsts)  # num_firsts at -4
            v.append(num_seconds)  # num_seconds at -3
            v.append(num_thirds)  # num_thirds at -2
            v.append(num_bads)  # num_bads at -1

        # iterate thru once more looking for the highest sum, then use num_firsts followed by num_seconds as tiebreaker
        # can still have multiple fan favorites
        fan_favorites = []
        favoritest_sum = 0
        favoritest_firsts = 0
        favoritest_seconds = 0
        for k, v in vote_dict.items():
            if len(fan_favorites) == 0:  # if list is empty, no need for comparisons
                fan_favorites.append(k)
                # save these now for comparison later - we could look it up again but the syntax starts to look bonkers
                favoritest_sum = v[-5]  # fifth last element is the sum
                favoritest_firsts = v[-4]  # fourth last element is the firsts
                favoritest_seconds = v[-3]  # third last element is the seconds
            elif (
                v[-5] > favoritest_sum
            ):  # if this survivor is more favorited, replace the existing favorites list
                fan_favorites = [k]
                favoritest_sum = v[-5]
                favoritest_firsts = v[-4]
                favoritest_seconds = v[-3]
            elif (
                v[-5] == favoritest_sum
            ):  # this survivor is as favorited, check for tiebreaks
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

        for (
            key,
            value,
        ) in (
            vote_dict.items()
        ):  # add survivor names to the dict for display purposes by fan_favorite_vote results
            value.append(Survivor.objects.get(id=key).name)  # look for that survivor

        return (
            favorite_survivors,
            vote_dict,
        )  # return only the survivors whose ID is in the fan_favorites list

    def fan_favorites_display(self):
        """ "Helper function for displaying the results of the fan_favorites function. Returns a list of formatted strings describing the votes each survivor received."""
        description = ["Points totals:"]
        vote_dict = self.fan_favorites()[1]
        vote_dict_sorted_by_sum = sorted(
            vote_dict.items(), key=lambda item: item[1][-6], reverse=True
        )  # sorts vote_dict.items by their values (1) & then the sixth-last item in that value (sum)
        # after appending name to end of list, sum is at -6, firsts at -5, seconds at -4, thirds at -3, bads at -2, & name at -1
        for key, value in vote_dict_sorted_by_sum:
            if self.rubric.fan_favorite_negative_votes:
                if value[-6] == 1:
                    description.append(
                        f"{value[-1]}: {value[-6]} point ({value[-5]} 1st, {value[-4]} 2nd, {value[-3]} 3rd, {value[-2]} bad votes)"
                    )
                else:
                    description.append(
                        f"{value[-1]}: {value[-6]} points ({value[-5]} 1st, {value[-4]} 2nd, {value[-3]} 3rd, {value[-2]} bad votes)"
                    )
            else:
                if value[-6] == 1:
                    description.append(
                        f"{value[-1]}: {value[-6]} point ({value[-5]} 1st, {value[-4]} 2nd, {value[-3]} 3rd votes)"
                    )
                else:
                    description.append(
                        f"{value[-1]}: {value[-6]} points ({value[-5]} 1st, {value[-4]} 2nd, {value[-3]} 3rd votes)"
                    )
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

    def predictions_display(self):
        """Returns a list of strings representing how each survivor with a prediction associated with them ended up placing."""
        survivor_dict = {}
        for t in self.team_set.all():
            if t.prediction_first:
                if t.prediction_first.id not in survivor_dict:
                    survivor_dict[t.prediction_first.id] = t.prediction_first
            if t.prediction_second:
                if t.prediction_second.id not in survivor_dict:
                    survivor_dict[t.prediction_second.id] = t.prediction_second
            if t.prediction_third:
                if t.prediction_third.id not in survivor_dict:
                    survivor_dict[t.prediction_third.id] = t.prediction_third

        results = []
        for key, value in survivor_dict.items():
            if value.status:  # survivor is still alive
                results.append(
                    f"{value.name} still alive, currently placed {value.placement_calq()}."
                )
            else:
                results.append(
                    f"{value.name} ended up placing {value.placement_calq()}."
                )

        return results

    def is_season_closed(self):
        """Returns True if today's date is on or after the season closing date, else False."""
        if self.season_close is None:
            return False  # season cannot close without a closing date
        else:
            return date.today() >= self.season_close

    def is_season_open(self):
        """Returns True if today's date is on or after the season opening date (or the opening date is null), else False."""
        return self.season_open is None or (date.today() >= self.season_open)

    def is_season_active(self):
        """Returns True if the season is currently running (past its opening date, before its closing date)"""
        return self.is_season_open() and not self.is_season_closed()

    def draft_order(self):
        """Returns a list of tuples of draft orders, with each entry the (draft position, team)"""
        draft_positions = {}
        for t in self.team_set.all():
            draft_markers = t.draft_order.split(
                ","
            )  # draft markers should be a comma-delimited string of numbers
            for draft_marker in draft_markers:
                try:
                    _draft_marker = int(draft_marker)
                except ValueError:
                    continue
                draft_positions[_draft_marker] = (
                    t  # this team is drafting at this marker, e.g. {1: team_1, 2: team_2}
                )
        return sorted(
            draft_positions.items()
        )  # sorts by key of the dictionary, which is handy

    def reorder_draft(self, type):
        """Assigns draft positions for teams within this season based on the type parameter provided
        Supported types:
        random: randomizes each round of the draft
        snake: randomizes the first round, then does reverse order of that, then reverse, etc.
        snake_with_random_tail: same as snake, but the final round is also randomized"""
        teams = self.team_set.all()
        number_of_teams = len(teams)
        number_of_survivors = len(self.survivor_set.all())
        number_of_rounds = (
            math.floor(number_of_survivors / number_of_teams)
            if number_of_teams > 0
            else 0
        )  # prevent divide by zero if no teams are present
        team_ordering = teams  # need to scope these variables outside of the below round loop so they don't reset per iteration
        team_ordering_backwards = team_ordering
        for team in teams:
            team.draft_order = (
                ""  # empty out each team's draft order in order to create a new one
            )
        if type != "free":
            for round in range(0, number_of_rounds):
                last_round = round == (number_of_rounds - 1)
                if round == 0 and (type == "snake" or type == "snake_random_tail"):
                    team_ordering = sorted(teams, key=lambda x: random.random())
                    team_ordering_backwards = reversed(
                        team_ordering
                    )  # not in place reversed copy of team_ordering
                if type == "random":  # if random, each round gets a randomized order
                    order = sorted(teams, key=lambda x: random.random())
                elif type == "snake" or type == "snake_random_tail":
                    if (
                        last_round and type == "snake_random_tail"
                    ):  # if snake_with_random tail & it's the last round, the round gets a random order
                        order = sorted(teams, key=lambda x: random.random())
                    elif (
                        round % 2 == 0
                    ):  # if either type of snake, even rounds use team_ordering, odd rounds use team_ordering_backwards
                        order = team_ordering
                    else:
                        order = team_ordering_backwards
                else:
                    order = teams  # if no matching type was provided, just leave the team ordering in place
                for pick, team in enumerate(order, start=1):
                    new_draft_order = (
                        number_of_teams * round
                    ) + pick  # so for the first pick of round 0, this would make 1.
                    # for the last pick of six teams in round 0, this would make 6
                    # for the last pick of six teams in round 2, this would make 18
                    if last_round:
                        team.draft_order += str(new_draft_order)
                    else:
                        team.draft_order += str(new_draft_order) + ","
        for team in teams:
            team.survivor_set.clear()  # given a new draft ordering, the draft should begin anew, meaning all previously drafted Survivors get undrafted
            team.save()  # save the new draft order for each team
        if type == "free":
            self.draft_marker = -1
        else:
            self.draft_marker = 1
        self.save()

    def max_team_size(self):
        """Determines max team size based on number of survivors in this draft divided by number of teams in this draft, floor"""
        num_survivors = len(self.survivor_set.all())
        num_teams = len(self.team_set.all())
        return math.floor(num_survivors / num_teams) if num_teams > 0 else 0


class Team(models.Model):
    season = models.ForeignKey(
        Season,
        on_delete=models.CASCADE,  # If a Season goes, so too goes every Team within it
        verbose_name="the season a team belongs to",
        null=True,
    )
    name = models.CharField(max_length=300, verbose_name="Team name", blank=False)
    captain = models.CharField(
        max_length=300,
        verbose_name="Captain name",
        blank=True,  # if unprovided, will default to User Name, followed by User Username
    )
    winner = models.BooleanField(default=False, null=False)

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,  # if the user a Team belongs to goes, just set its owner back to null
        verbose_name="the user a team belongs to",
        null=True,
    )

    fan_favorite_first = models.ForeignKey(
        "Survivor",  # trick the compiler into letting us reference a class not yet defined
        on_delete=models.SET_NULL,
        verbose_name="First place fan favorite vote submitted by this team",
        null=True,  # a team can forgo a vote
        related_name="+",  # no need for backwards relating a fan fave survivor to the team that voted it
        blank=True,
    )
    fan_favorite_second = models.ForeignKey(
        "Survivor",  # trick the compiler into letting us reference a class not yet defined
        on_delete=models.SET_NULL,
        verbose_name="Second place fan favorite vote submitted by this team",
        null=True,  # a team can forgo a vote
        related_name="+",  # no need for backwards relating a fan fave survivor to the team that voted it
        blank=True,
    )
    fan_favorite_third = models.ForeignKey(
        "Survivor",  # trick the compiler into letting us reference a class not yet defined
        on_delete=models.SET_NULL,
        verbose_name="Third place fan favorite vote submitted by this team",
        null=True,  # a team can forgo a vote
        related_name="+",  # no need for backwards relating a fan fave survivor to the team that voted it
        blank=True,
    )
    fan_favorite_bad = models.ForeignKey(
        "Survivor",  # trick the compiler into letting us reference a class not yet defined
        on_delete=models.SET_NULL,
        verbose_name="Negative place fan favorite vote submitted by this team",
        null=True,  # a team can forgo a vote
        related_name="+",  # no need for backwards relating a fan fave survivor to the team that voted it
        blank=True,
    )

    prediction_first = models.ForeignKey(
        "Survivor",  # trick the compiler into letting us reference a class not yet defined
        on_delete=models.SET_NULL,
        verbose_name="First place prediction for this season",
        null=True,  # a team can forgo a vote
        related_name="+",  # no need for backwards relating a prediction to the team that voted it
        blank=True,
    )
    prediction_second = models.ForeignKey(
        "Survivor",  # trick the compiler into letting us reference a class not yet defined
        on_delete=models.SET_NULL,
        verbose_name="Second place prediction for this season",
        null=True,  # a team can forgo a vote
        related_name="+",  # no need for backwards relating a prediction to the team that voted it
        blank=True,
    )
    prediction_third = models.ForeignKey(
        "Survivor",  # trick the compiler into letting us reference a class not yet defined
        on_delete=models.SET_NULL,
        verbose_name="Third place prediction for this season",
        null=True,  # a team can forgo a vote
        related_name="+",  # no need for backwards relating a prediction to the team that voted it
        blank=True,
    )
    draft_order = models.CharField(
        max_length=300,
        verbose_name="Comma-delimited list of positions this team can draft in",
        blank=True,
    )

    draft_owner = models.BooleanField(
        default=False,
        verbose_name="Draft Owner: whether this Team has administrative access to the draft & draft ordering",
        null=False,
    )

    def clean(self):
        errors = []

        if self.season is not None:
            if (
                self.fan_favorite_first is not None
                and self.fan_favorite_first == self.fan_favorite_second
            ):
                errors.append(
                    ValidationError(
                        _("First and second vote cannot be the same"), code="matched12"
                    )
                )
            if (
                self.fan_favorite_first is not None
                and self.fan_favorite_first == self.fan_favorite_third
            ):
                errors.append(
                    ValidationError(
                        _("First and third vote cannot be the same"), code="matched13"
                    )
                )
            if (
                self.fan_favorite_first is not None
                and self.fan_favorite_first == self.fan_favorite_bad
            ):
                errors.append(
                    ValidationError(
                        _("First and bad vote cannot be the same"), code="matched14"
                    )
                )
            if (
                self.fan_favorite_second is not None
                and self.fan_favorite_second == self.fan_favorite_third
            ):
                errors.append(
                    ValidationError(
                        _("Second and third vote cannot be the same"), code="matched23"
                    )
                )
            if (
                self.fan_favorite_second is not None
                and self.fan_favorite_second == self.fan_favorite_bad
            ):
                errors.append(
                    ValidationError(
                        _("Second and bad vote cannot be the same"), code="matched24"
                    )
                )
            if (
                self.fan_favorite_third is not None
                and self.fan_favorite_third == self.fan_favorite_bad
            ):
                errors.append(
                    ValidationError(
                        _("Third and bad vote cannot be the same"), code="matched34"
                    )
                )

            if (
                not self.season.rubric.fan_favorite_self_votes
            ):  # if self votes are disallowed, validate them
                if (
                    self.fan_favorite_first is not None
                    and self.fan_favorite_first.team == self
                ):
                    errors.append(
                        ValidationError(
                            _("First vote cannot be for a player on your own team"),
                            code="sameTeam1",
                        )
                    )
                if (
                    self.fan_favorite_second is not None
                    and self.fan_favorite_second.team == self
                ):
                    errors.append(
                        ValidationError(
                            _("Second vote cannot be for a player on your own team"),
                            code="sameTeam2",
                        )
                    )
                if (
                    self.fan_favorite_third is not None
                    and self.fan_favorite_third.team == self
                ):
                    errors.append(
                        ValidationError(
                            _("Third vote cannot be for a player on your own team"),
                            code="sameTeam3",
                        )
                    )
                if (
                    self.fan_favorite_bad is not None
                    and self.fan_favorite_bad.team == self
                ):
                    errors.append(
                        ValidationError(
                            _("Bad vote cannot be for a player on your own team"),
                            code="sameTeam4",
                        )
                    )

            if (
                self.prediction_first is not None
                and self.prediction_first == self.prediction_second
            ):
                errors.append(
                    ValidationError(
                        _("First and second prediction cannot be the same"),
                        code="predictionMatched12",
                    )
                )
            if (
                self.prediction_first is not None
                and self.prediction_first == self.prediction_third
            ):
                errors.append(
                    ValidationError(
                        _("First and third prediction cannot be the same"),
                        code="predictionMatched13",
                    )
                )
            if (
                self.prediction_second is not None
                and self.prediction_second == self.prediction_third
            ):
                errors.append(
                    ValidationError(
                        _("Second and third prediction cannot be the same"),
                        code="predictionMatched23",
                    )
                )

        if len(errors) > 0:
            raise ValidationError(errors)

    def __str__(self) -> str:
        """Returns a string representation of a Survivor Team"""
        if self.season:
            return f"Team name: {self.name}. Captain: {self.captain}. Season: {self.season.name}."
        else:
            return f"Team name: {self.name}. Captain: {self.captain}."

    def points(self) -> int:
        """Returns the sum of all points earned by Survivors within this team"""
        total = 0
        for s in Survivor.objects.filter(team=self):
            total += s.points(self.season)[0]
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

    def confessionals(self) -> int:
        """Returns the sum of all confessionals done by Survivors within this team"""
        total = 0
        for s in self.survivor_set.all():
            total += s.confessionals
        return total

    def lost(self) -> bool:
        """If season is over, returns True if this team won, else False"""
        """Returns True if all survivors on this team have been eliminated, & this team's points total (plus fan favorite value) is lower than some other team's"""
        if self.season and self.season.is_season_closed():
            return not self.winner
        elif all(not s.status for s in self.survivor_set.all()):
            if self.season and self.season.rubric:
                fan_favorite_points = self.season.rubric.fan_favorite
            else:
                fan_favorite_points = 0
            my_theoretical_points = (
                self.points() + fan_favorite_points
            )  # fan favorite points are the only thing we could theoretically still earn
            if self.season:
                for t in self.season.team_set.all():
                    if t is self:
                        continue
                    elif (
                        t.points() > my_theoretical_points
                    ):  # if any other team has more points than myself, & all my survivors are out, I have officially lost, return True
                        return True
        return False

    def next_pick(self) -> int | None:
        """Returns next pick in the team's draft order based on survivor_set, or None if no picks left.
        A value of -1 indicates draft_order was empty, but the team still has picks left.
        """
        if (
            self.draft_order == ""
        ):  # in the event a draft order is undefined, can still draft if draft_marker is <= 0. This distinguishes from None for a full team
            return -1
        num_team_members = len(self.survivor_set.all())
        picks = self.draft_order.split(",")
        if not self.season:  # if season does not exist, neither does next pick
            return None
        elif (
            num_team_members >= self.season.max_team_size()
        ):  # if I already have equal or more team members than the max team size based on participating teams
            return None
        if num_team_members >= len(
            picks
        ):  # if I already have equal or more team members than picks, I've already made all available picks
            return None
        else:  # else, return the next entry in the picks list (because of zero indexing, this is just index num_team_members)
            return int(picks[num_team_members])

    def can_pick(self) -> tuple[bool, str]:
        """Returns a boolean indicating whether I can currently pick, & a string containing what to say if I can't"""
        next_pick = self.next_pick()
        if next_pick is None:  # team is full, cannot draft
            pick_text = "It's not your turn to draft. You appear to have no picks left."
            _can_pick = False
        elif not self.season:
            pick_text = "Team is not part of a season. Can't pick without a season."
            _can_pick = False
        elif self.season.draft_marker < 0:  # not maintaining draft order, so can draft
            pick_text = "Draft is free for all. You can draft."
            _can_pick = True
        elif self.season.draft_marker == 0:  # not tracking draft marker, so can draft
            pick_text = "Draft marker tracking disabled. You can draft."
            _can_pick = True
        else:  # draft_marker is tracked, team is not full
            if self.season.draft_marker == next_pick:
                pick_text = "Draft marker matches your next pick. You can draft."
                _can_pick = True
            elif self.season.draft_marker > next_pick:
                pick_text = "Draft marker is after your next pick. You're behind - draft to catch up."
                _can_pick = True
            else:
                pick_text = "It's not your turn to draft. Current pick is at {}, whereas your next pick is {}".format(
                    self.season.draft_marker, next_pick
                )
                _can_pick = False
        return (_can_pick, pick_text)


class Tribe(models.Model):
    season = models.ManyToManyField(
        Season,
        verbose_name="The seasons associated with this tribe",
        blank=True,
        default=None,
    )
    name = models.CharField(max_length=100)
    color = models.CharField(
        max_length=100,
        verbose_name="the hex code for the color associated with this tribe",
    )

    def points(self, season) -> int:
        """Returns an integer representing the sum of Survivor points of Survivors within this tribe for the given season"""
        total = 0
        for survivor in self.survivor_set.all():
            total += survivor.points(season)[0]
        return total


class Survivor(models.Model):
    season = models.ManyToManyField(
        Season, verbose_name="a season a Survivor belongs to", blank=True, default=None
    )
    name = models.CharField(max_length=100)
    status = models.BooleanField(
        default=False,
        null=False,
        verbose_name="Elimination Status - False for eliminated, True for surviving",
    )
    team = models.ManyToManyField(
        Team,
        verbose_name="a team that recruited this survivor",
        blank=True,
        default=None,
    )
    tribe = models.ForeignKey(
        Tribe,
        on_delete=models.SET_NULL,
        verbose_name="the tribe this survivor currently belongs to",
        null=True,
        blank=True,
        default=None,
    )
    idols = models.IntegerField(default=0, null=False)
    advantages = models.IntegerField(default=0, null=False)
    immunities = models.IntegerField(default=0, null=False)
    jury_number = models.IntegerField(default=0, null=False)
    placement = models.IntegerField(
        default=0, null=False
    )  # place eliminated, where 0 is not yet eliminated, 1 is first, high number is last
    confessionals = models.IntegerField(default=0, null=False)
    fan_favorite = models.BooleanField(
        default=False, null=False
    )  # this is calculated, but we don't want to run the calqs every time, so still saving it when Season.fan_favorites() runs
    finalist = models.BooleanField(
        default=False, null=False
    )  # Winner is an upgraded finalist
    winner = models.BooleanField(default=False, null=False)
    pic = models.ImageField(
        default=None, null=True, blank=True
    )  # a null image will use a default blank image
    pic_full = models.ImageField(
        default=None, null=True, blank=True
    )  # larger image used by Survivor page, can also be null

    def __str__(self) -> str:
        """Returns a string representation of a Survivor contestant"""
        _status = "Surviving" if self.status else "Eliminated"
        # return f"Contestant name: {self.name}. Team: {self.team}. Status: {_status}"
        return self.name

    def points(
        self, season
    ) -> tuple[
        int, str
    ]:  # turn into a tuple - first the integer, second the descriptor string?
        """Returns a two-element tuple, first element is total points earned by this Survivor, second element is a string describing that math"""
        if season in self.season.all():
            rubric = season.rubric
        else:
            return 0, "Could not find a rubric to score this survivor against."
        total = 0
        description = "POINTS BREAKDOWN\nPoints Earned * Rubric Value = Score\n"

        if (
            self.idols > 0
        ):  # cannot award idol points if at least one idol hasn't been earned
            most_idol_winners = season.most_idols()
            most_idols = (
                self in most_idol_winners
            )  # if self is one of the Survivors with the most idols
            if most_idols:
                if (
                    len(most_idol_winners) > 1 and rubric.idols_tie_split
                ):  # if there is a tie for most idol winners and the rubric says to split ties
                    total += math.ceil(rubric.idols / len(most_idol_winners))
                    description += f"Most idol points (tie): Ceiling({rubric.idols} / {len(most_idol_winners)}) = {math.ceil(rubric.idols / len(most_idol_winners))}\n"
                else:  # else just give full rubric idols points
                    total += rubric.idols
                    description += (
                        f"Most idol points: {rubric.idols} = {rubric.idols}\n"
                    )

        if (
            self.immunities > 0
        ):  # cannot award immunity points if at least one immunity hasn't been earned
            most_immunities_winners = season.most_immunities()
            most_immunities = (
                self in most_immunities_winners
            )  # if self is one of the Survivors with the most immunities
            if most_immunities:
                if (
                    len(most_immunities_winners) > 1 and rubric.immunities_tie_split
                ):  # if there is a tie for most immunities and the rubric says to split ties
                    total += math.ceil(rubric.immunities / len(most_immunities_winners))
                    description += f"Most immunities points (tie): Ceiling({rubric.immunities} / {len(most_immunities_winners)}) = {math.ceil(rubric.immunities / len(most_immunities_winners))}\n"
                else:  # else just give full rubric immunities points
                    total += rubric.immunities
                    description += f"Most individual immunities: {rubric.immunities} = {rubric.immunities}\n"

        if (
            self.confessionals > 0
        ):  # cannot award confessional points if they haven't even been in one
            most_confessional_winners = season.most_confessionals()
            most_confessionals = (
                self in most_confessional_winners
            )  # if self is one of the Survivors with the most confessionals
            if most_confessionals:
                if (
                    len(most_confessional_winners) > 1
                    and rubric.confessionals_tie_split
                ):  # if there is a tie for most confessionals and the rubric says to split ties
                    total += math.ceil(
                        rubric.confessionals / len(most_confessional_winners)
                    )
                    description += f"Most confessionals points (tie): Ceiling({rubric.confessionals} / {len(most_confessional_winners)}) = {math.ceil(rubric.confessionals / len(most_confessional_winners))}\n"
                else:  # else just give full rubric confessional points
                    total += rubric.confessionals
                    description += f"Most confessionals: {rubric.confessionals} = {rubric.confessionals}\n"

        if (
            self.status
        ):  # if alive, jury points are dictated by highest-scoring eliminated survivor
            jury_points = season.jury_number()
            total += jury_points * rubric.jury_number
            description += f"Jury number: {jury_points} * {rubric.jury_number} = {jury_points * rubric.jury_number}\n"
        else:  # if eliminated, jury points are only dictated by own entry
            total += self.jury_number * rubric.jury_number
            description += f"Jury number: {self.jury_number} * {rubric.jury_number} = {self.jury_number * rubric.jury_number} \n"

        if not self.status:  # if not alive, was I eliminated first?
            s = self.season.first()
            if s and self.placement == len(s.survivor_set.all()):
                total += rubric.pity_point
                description += f"Pity point: {rubric.pity_point}\n"

        if self.fan_favorite:
            total += rubric.fan_favorite
            description += f"Fan favorite: {self.fan_favorite} * {rubric.fan_favorite} = {rubric.fan_favorite}\n"
        if self.finalist:
            if self.winner:
                total += self.winner * rubric.winner
                description += (
                    f"Winner: {self.winner} * {rubric.winner} = {rubric.winner}"
                )
            else:
                total += self.finalist * rubric.finalist
                description += f"Finalist: {self.finalist} * {rubric.finalist} = {self.finalist * rubric.finalist}"
        return total, description.strip()  # remove trailing newline if present

    def placement_calq(self):
        """Returns an integer representing either the place eliminated or, if not yet eliminated, one better than the last person eliminated
        Finalists can come in second if they did not win, but did receive more votes then the other loser
        """
        if (
            self.placement == 0
        ):  # a value of 0 indicates the survivor did not explictly 'place', meaning they're still alive & receive one better than the last eliminated survivor
            return self.season.all().first().placement()
        else:  # any nonzero value is a valid placement & is returned as such
            return self.placement
