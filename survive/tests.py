from django.test import TestCase
from survive.models import *

class SurvivorTestCase(TestCase):
    def setup(self):
        # without additional arguments, defaults of 2 for idols & true for idol split,
        # 2 for immunities & true for immunities split,
        # 1 for jury number,
        # 2 for fan favorite,
        # 2 for finalist,
        # 5 for winner
        r = Rubric.objects.create()
        s = Season.objects.create(name = "TestSeason", rubric = r)
        t = Team.objects.create(name = "TestTeam", captain = "TestCaptain", season = s)

    def setup_other_survivor(self):
        # as above, but also adds a default survivor
        self.setup()
        season = Season.objects.get(name = "TestSeason")
        team = Team.objects.get(id = 1)
        survivor = Survivor.objects.create( # this is a 'base' Survivor, fresh off the boat, no points earned
            season = season,
            team = team,
            name = "Test Player",
            status = False,
            idols = 0,
            advantages = 0,
            immunities = 0,
            jury_number = 0,
            confessionals = 0,
            fan_favorite = False,
            finalist = False,
            winner = False
        )

    def test_points_sum_simple(self):
        """Survivor points sum correctly. This tests for individual accomplishments, not comparisons (most idols etc.)"""

        self.setup()

        season = Season.objects.get(name = "TestSeason")
        team = Team.objects.get(id = 1)
        survivor = Survivor.objects.create( # this is a 'base' Survivor, fresh off the boat, no points earned
            season = season,
            team = team,
            name = "Test Player",
            status = False,
            idols = 0,
            advantages = 0,
            immunities = 0,
            jury_number = 0,
            confessionals = 0,
            fan_favorite = False,
            finalist = False,
            winner = False
        )

        self.assertEqual(survivor.points()[0], 0)

        survivor.finalist = True

        self.assertEqual(survivor.points()[0], 2)

        survivor.winner = True

        self.assertEqual(survivor.points()[0], 5) # winner should be worth 5, not (Finalist + Winner) = 7

        survivor.fan_favorite = True

        self.assertEqual(survivor.points()[0], 7)

    def test_points_sum_comparisons_no_ties(self):
        """Survivor points sum correctly. This tests whether points calq correctly when determining 'most of' awards. No ties here"""
        self.setup_other_survivor()
        
        season = Season.objects.filter(pk=1).first()
        team = Team.objects.filter(pk=1).first()
        rubric = season.rubric
        rubric.idols_tie_split = False
        rubric.immunities_tie_split = False
        rubric.save() # must save changes made
        survivor = Survivor.objects.create(
            season = season,
            team = team,
            name = "Test Player 2",
            status = False,
            idols = 0,
            advantages = 0,
            immunities = 0,
            jury_number = 0,
            confessionals = 0,
            fan_favorite = False,
            finalist = False,
            winner = False
        )

        other_survivor = Survivor.objects.get(name = "Test Player") # get other survivor for comparison

        survivor.idols = 1
        survivor.save()

        self.assertEqual(survivor.points()[0], 2) # now that I have an idol on the board, I should win the idol points

        other_survivor.idols = 1
        other_survivor.save()

        self.assertEqual(survivor.points()[0], 2) # because ties don't split points, we should still have 2

        survivor.immunities = 1
        survivor.save()

        self.assertEqual(survivor.points()[0], 4) # as above, should now have idol & immunity points

        other_survivor.immunities = 1
        other_survivor.save()

        self.assertEqual(survivor.points()[0], 4) # as above, no ties, therefore still have both points

    def test_points_sum_comparisons_only_ties(self):
        """Survivor points sum correctly. This tests whether points calq correctly when determining 'most of' awards. Ties only here"""
        self.setup_other_survivor()
        
        season = Season.objects.filter(pk=1).first()
        team = Team.objects.filter(pk=1).first()
        survivor = Survivor.objects.create(
            season = season,
            team = team,
            name = "Test Player 2",
            status = False,
            idols = 0,
            advantages = 0,
            immunities = 0,
            jury_number = 0,
            confessionals = 0,
            fan_favorite = False,
            finalist = False,
            winner = False
        )

        other_survivor = Survivor.objects.get(name = "Test Player") # get other survivor for comparison

        survivor.idols = 1
        survivor.save()

        self.assertEqual(survivor.points()[0], 2) # now that I have an idol on the board, I should win the idol points

        other_survivor.idols = 1
        other_survivor.save()

        self.assertEqual(survivor.points()[0], 1) # because ties split points, we should now have 1

        survivor.immunities = 1
        survivor.save()

        self.assertEqual(survivor.points()[0], 3)

        other_survivor.immunities = 1
        other_survivor.save()

        self.assertEqual(survivor.points()[0], 2)

    def test_season_jury_number(self):
        """Season jury number returns highest jury number amongst eliminated Survivors."""
        self.setup()
        
        season = Season.objects.filter(pk=1).first()
        team = Team.objects.filter(pk=1).first()
        survivor1 = Survivor.objects.create(
            season = season,
            team = team,
            name = "Test Player 2",
            status = False,
            idols = 0,
            advantages = 0,
            immunities = 0,
            jury_number = 2,
            confessionals = 0,
            fan_favorite = False,
            finalist = False,
            winner = False
        )
        survivor2 = Survivor.objects.create(
            season = season,
            team = team,
            name = "Test Player 2",
            status = True,
            idols = 0,
            advantages = 0,
            immunities = 0,
            jury_number = 0,
            confessionals = 0,
            fan_favorite = False,
            finalist = False,
            winner = False
        )
        survivor3 = Survivor.objects.create(
            season = season,
            team = team,
            name = "Test Player 2",
            status = False,
            idols = 0,
            advantages = 0,
            immunities = 0,
            jury_number = 6,
            confessionals = 0,
            fan_favorite = False,
            finalist = False,
            winner = False
        )

        self.assertEqual(6, season.jury_number())

    def test_season_placement(self):
        """Season placement returns the lowest placement amongst eliminated Survivors, minus one"""
        self.setup()
        
        season = Season.objects.filter(pk=1).first()
        team = Team.objects.filter(pk=1).first()
        survivor1 = Survivor.objects.create(
            season = season,
            team = team,
            name = "Test Player 2",
            status = False,
            idols = 0,
            advantages = 0,
            immunities = 0,
            jury_number = 2,
            confessionals = 0,
            fan_favorite = False,
            finalist = False,
            winner = False,
            placement = 3
        )
        survivor2 = Survivor.objects.create(
            season = season,
            team = team,
            name = "Test Player 2",
            status = True,
            idols = 0,
            advantages = 0,
            immunities = 0,
            jury_number = 0,
            confessionals = 0,
            fan_favorite = False,
            finalist = False,
            winner = False
        )
        survivor3 = Survivor.objects.create(
            season = season,
            team = team,
            name = "Test Player 2",
            status = False,
            idols = 0,
            advantages = 0,
            immunities = 0,
            jury_number = 6,
            confessionals = 0,
            fan_favorite = False,
            finalist = False,
            winner = False,
            placement = 2
        )

        self.assertEqual(1, season.placement())

