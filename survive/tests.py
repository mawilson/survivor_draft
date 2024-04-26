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
        s = Season.objects.create(name="TestSeason", rubric=r)
        t = Team.objects.create(name="TestTeam", captain="TestCaptain", season=s)

    def setup_other_survivor(self):
        # as above, but also adds a default survivor
        self.setup()
        season = Season.objects.get(name="TestSeason")
        team = Team.objects.get(id=1)
        survivor = Survivor.objects.create(  # this is a 'base' Survivor, fresh off the boat, no points earned
            name="Test Player",
            status=False,
            idols=0,
            advantages=0,
            immunities=0,
            jury_number=0,
            confessionals=0,
            fan_favorite=False,
            finalist=False,
            winner=False,
        )
        survivor.season.add(season)
        survivor.team.add(team)

    def test_points_sum_simple(self):
        """Survivor points sum correctly. This tests for individual accomplishments, not comparisons (most idols etc.)"""

        self.setup()

        season = Season.objects.get(name="TestSeason")
        team = Team.objects.get(id=1)
        survivor = Survivor.objects.create(  # this is a 'base' Survivor, fresh off the boat, no points earned
            name="Test Player",
            status=False,
            idols=0,
            advantages=0,
            immunities=0,
            jury_number=0,
            confessionals=0,
            fan_favorite=False,
            finalist=False,
            winner=False,
        )

        survivor.season.add(season)
        survivor.team.add(team)

        self.assertEqual(survivor.points(season)[0], 0)

        survivor.finalist = True

        self.assertEqual(survivor.points(season)[0], 2)

        survivor.winner = True

        self.assertEqual(
            survivor.points(season)[0], 5
        )  # winner should be worth 5, not (Finalist + Winner) = 7

        survivor.fan_favorite = True

        self.assertEqual(survivor.points(season)[0], 7)

    def test_points_zero_start(self):
        """Survivor points sum to zero when nothing has been accomplished."""

        self.setup()

        season = Season.objects.get(name="TestSeason")
        team = Team.objects.get(id=1)
        survivor = Survivor.objects.create(  # this is a 'base' Survivor, fresh off the boat, no points earned
            name="Test Player",
            status=True,
            idols=0,
            advantages=0,
            immunities=0,
            jury_number=0,
            confessionals=0,
            fan_favorite=False,
            finalist=False,
            winner=False,
        )

        survivor.season.add(season)
        survivor.team.add(team)

        self.assertEqual(survivor.points(season)[0], 0)

        survivor2 = Survivor.objects.create(  # this is a 'base' Survivor, fresh off the boat, no points earned
            name="Test Player2",
            status=True,
            idols=0,
            advantages=0,
            immunities=0,
            jury_number=0,
            confessionals=0,
            fan_favorite=False,
            finalist=False,
            winner=False,
        )

        survivor2.season.add(season)
        survivor2.team.add(team)

        self.assertEqual(survivor.points(season)[0], 0)

        survivor3 = Survivor.objects.create(  # this is a 'base' Survivor, fresh off the boat, no points earned
            name="Test Player3",
            status=False,  # this survivor has been eliminated
            idols=0,
            advantages=0,
            immunities=0,
            jury_number=0,
            confessionals=0,
            fan_favorite=False,
            finalist=False,
            winner=False,
        )

        survivor3.season.add(season)
        survivor3.team.add(team)

        self.assertEqual(
            survivor.points(season)[0], 0
        )  # survivor3 has been eliminated, but their jury number was 0, so jury_number points should still be 0

        survivor4 = Survivor.objects.create(  # this is a 'base' Survivor, fresh off the boat, no points earned
            name="Test Player4",
            status=False,  # this survivor has been eliminated
            idols=0,
            advantages=0,
            immunities=0,
            jury_number=1,
            confessionals=0,
            fan_favorite=False,
            finalist=False,
            winner=False,
        )

        survivor4.season.add(season)
        survivor4.team.add(team)

        self.assertEqual(
            survivor.points(season)[0], 2
        )  # survivor4 has been eliminated, & their jury number was 1 (nonzero), so jury_number points should be 2

    def test_points_sum_comparisons_no_ties(self):
        """Survivor points sum correctly. This tests whether points calq correctly when determining 'most of' awards. No ties here"""
        self.setup_other_survivor()

        season = Season.objects.filter(pk=1).first()
        team = Team.objects.filter(pk=1).first()
        rubric = season.rubric
        rubric.idols_tie_split = False
        rubric.immunities_tie_split = False
        rubric.save()  # must save changes made
        survivor = Survivor.objects.create(
            name="Test Player 2",
            status=False,
            idols=0,
            advantages=0,
            immunities=0,
            jury_number=0,
            confessionals=0,
            fan_favorite=False,
            finalist=False,
            winner=False,
        )

        survivor.season.add(season)
        survivor.team.add(team)

        other_survivor = Survivor.objects.get(
            name="Test Player"
        )  # get other survivor for comparison

        survivor.idols = 1
        survivor.save()

        self.assertEqual(
            survivor.points(season)[0], 2
        )  # now that I have an idol on the board, I should win the idol points

        other_survivor.idols = 1
        other_survivor.save()

        self.assertEqual(
            survivor.points(season)[0], 2
        )  # because ties don't split points, we should still have 2

        survivor.immunities = 1
        survivor.save()

        self.assertEqual(
            survivor.points(season)[0], 4
        )  # as above, should now have idol & immunity points

        other_survivor.immunities = 1
        other_survivor.save()

        self.assertEqual(
            survivor.points(season)[0], 4
        )  # as above, no ties, therefore still have both points

    def test_points_sum_comparisons_only_ties(self):
        """Survivor points sum correctly. This tests whether points calq correctly when determining 'most of' awards. Ties only here"""
        self.setup_other_survivor()

        season = Season.objects.filter(pk=1).first()
        team = Team.objects.filter(pk=1).first()
        survivor = Survivor.objects.create(
            name="Test Player 2",
            status=False,
            idols=0,
            advantages=0,
            immunities=0,
            jury_number=0,
            confessionals=0,
            fan_favorite=False,
            finalist=False,
            winner=False,
        )

        survivor.season.add(season)
        survivor.team.add(team)

        other_survivor = Survivor.objects.get(
            name="Test Player"
        )  # get other survivor for comparison

        survivor.idols = 1
        survivor.save()

        self.assertEqual(
            survivor.points(season)[0], 2
        )  # now that I have an idol on the board, I should win the idol points

        other_survivor.idols = 1
        other_survivor.save()

        self.assertEqual(
            survivor.points(season)[0], 1
        )  # because ties split points, we should now have 1

        survivor.immunities = 1
        survivor.save()

        self.assertEqual(survivor.points(season)[0], 3)

        other_survivor.immunities = 1
        other_survivor.save()

        self.assertEqual(survivor.points(season)[0], 2)

    def test_season_jury_number(self):
        """Season jury number returns highest jury number amongst eliminated Survivors."""
        self.setup()

        season = Season.objects.filter(pk=1).first()
        team = Team.objects.filter(pk=1).first()
        survivor1 = Survivor.objects.create(
            name="Test Player 2",
            status=False,
            idols=0,
            advantages=0,
            immunities=0,
            jury_number=2,
            confessionals=0,
            fan_favorite=False,
            finalist=False,
            winner=False,
        )
        survivor1.season.add(season)
        survivor1.team.add(team)
        survivor2 = Survivor.objects.create(
            name="Test Player 2",
            status=True,
            idols=0,
            advantages=0,
            immunities=0,
            jury_number=0,
            confessionals=0,
            fan_favorite=False,
            finalist=False,
            winner=False,
        )
        survivor2.season.add(season)
        survivor2.team.add(team)
        survivor3 = Survivor.objects.create(
            name="Test Player 2",
            status=False,
            idols=0,
            advantages=0,
            immunities=0,
            jury_number=6,
            confessionals=0,
            fan_favorite=False,
            finalist=False,
            winner=False,
        )
        survivor3.season.add(season)
        survivor3.team.add(team)

        survivor4 = Survivor.objects.create(name="test")
        survivor5 = Survivor.objects.create(name="test")
        survivor6 = Survivor.objects.create(name="test")
        survivor7 = Survivor.objects.create(name="test")
        survivor8 = Survivor.objects.create(name="test")
        survivor9 = Survivor.objects.create(name="test")
        survivor10 = Survivor.objects.create(name="test")
        survivor11 = Survivor.objects.create(name="test")
        survivor4.season.add(season)
        survivor5.season.add(season)
        survivor6.season.add(season)
        survivor7.season.add(season)
        survivor8.season.add(season)
        survivor9.season.add(season)
        survivor10.season.add(season)
        survivor11.season.add(season)

        self.assertEqual(7, season.jury_number())

    def test_season_placement(self):
        """Season placement returns the lowest placement amongst eliminated Survivors, minus one"""
        self.setup()

        season = Season.objects.filter(pk=1).first()
        team = Team.objects.filter(pk=1).first()
        survivor1 = Survivor.objects.create(
            name="Test Player 2",
            status=False,
            idols=0,
            advantages=0,
            immunities=0,
            jury_number=2,
            confessionals=0,
            fan_favorite=False,
            finalist=False,
            winner=False,
            placement=3,
        )
        survivor1.season.add(season)
        survivor1.team.add(team)
        survivor2 = Survivor.objects.create(
            name="Test Player 2",
            status=True,
            idols=0,
            advantages=0,
            immunities=0,
            jury_number=0,
            confessionals=0,
            fan_favorite=False,
            finalist=False,
            winner=False,
        )
        survivor2.season.add(season)
        survivor2.team.add(team)
        survivor3 = Survivor.objects.create(
            name="Test Player 2",
            status=False,
            idols=0,
            advantages=0,
            immunities=0,
            jury_number=6,
            confessionals=0,
            fan_favorite=False,
            finalist=False,
            winner=False,
            placement=2,
        )
        survivor3.season.add(season)
        survivor3.team.add(team)

        self.assertEqual(1, season.placement())

    def test_season_fan_favorites(self):
        """Fan favorites are correctly deduced based on votes cast by teams"""
        r = Rubric.objects.create()
        s = Season.objects.create(name="TestSeason", rubric=r)

        t1 = Team.objects.create(name="Team1", captain="Captain1", season=s)
        t2 = Team.objects.create(name="Team2", captain="Captain2", season=s)
        t3 = Team.objects.create(name="Team3", captain="Captain3", season=s)

        s1 = Survivor.objects.create(
            name="Test Player Team1",
            status=False,
            idols=0,
            advantages=0,
            immunities=0,
            jury_number=0,
            confessionals=0,
            fan_favorite=False,
            finalist=False,
            winner=False,
        )
        s1.season.add(s)
        s1.team.add(t1)
        s2 = Survivor.objects.create(
            name="Test Player Team2",
            status=False,
            idols=0,
            advantages=0,
            immunities=0,
            jury_number=0,
            confessionals=0,
            fan_favorite=False,
            finalist=False,
            winner=False,
        )
        s2.season.add(s)
        s2.team.add(t2)
        s3 = Survivor.objects.create(
            name="Test Player2 Team2",
            status=False,
            idols=0,
            advantages=0,
            immunities=0,
            jury_number=0,
            confessionals=0,
            fan_favorite=False,
            finalist=False,
            winner=False,
        )
        s3.season.add(s)
        s3.team.add(t2)

        t1.fan_favorite_first = s1
        t1.fan_favorite_second = s2
        t1.fan_favorite_third = s3
        t1.save()

        t2.fan_favorite_first = s2  # s2 has 5 points
        t2.fan_favorite_second = s3  # s3 has 3 points
        t2.fan_favorite_third = s1  # s1 has 4 points
        t2.save()

        fan_favorites = s.fan_favorites(
            save=True
        )  # having cast the fan favorite votes, need to recalq the fan favorites
        # the s's are stale now, need to get 'em all again
        survivors = s.survivor_set.all()
        s1 = survivors[0]
        s2 = survivors[1]
        s3 = survivors[2]

        self.assertTrue(s2.fan_favorite)
        self.assertFalse(s1.fan_favorite)
        self.assertFalse(s3.fan_favorite)

        t1.fan_favorite_second = None  # s2 now has 3 points
        t1.save()

        fan_favorites = s.fan_favorites(save=True)
        # the s's are stale now, need to get 'em all again
        survivors = s.survivor_set.all()
        s1 = survivors[0]
        s2 = survivors[1]
        s3 = survivors[2]

        self.assertTrue(s1.fan_favorite)
        self.assertFalse(s2.fan_favorite)
        self.assertFalse(s3.fan_favorite)

        t3.fan_favorite_bad = s1  # s1 has 3 points; now all three have 3 points. Both s1 & s2 have a first place vote, no second places, so both have fan favorite
        t3.save()

        fan_favorites = s.fan_favorites(save=True)
        # the s's are stale now, need to get 'em all again
        survivors = s.survivor_set.all()
        s1 = survivors[0]
        s2 = survivors[1]
        s3 = survivors[2]

        self.assertTrue(s1.fan_favorite)
        self.assertTrue(s2.fan_favorite)
        self.assertFalse(s3.fan_favorite)

        t1.fan_favorite_first = s1
        t2.fan_favorite_first = s2
        t3.fan_favorite_first = None

        t1.fan_favorite_second = s2
        t2.fan_favorite_second = None
        t3.fan_favorite_second = s3

        t1.fan_favorite_third = s1
        t2.fan_favorite_third = s1
        t3.fan_favorite_third = s3

        t3.fan_favorite_bad = None  # s1 & s2 have five points, & each has a first place, but s2 has a second place, so only s2 gets fan favorite

        t1.save()
        t2.save()
        t3.save()

        fan_favorites = s.fan_favorites(save=True)
        # the s's are stale now, need to get 'em all again
        survivors = s.survivor_set.all()
        s1 = survivors[0]
        s2 = survivors[1]
        s3 = survivors[2]

        self.assertFalse(s1.fan_favorite)
        self.assertTrue(s2.fan_favorite)
        self.assertFalse(s3.fan_favorite)
