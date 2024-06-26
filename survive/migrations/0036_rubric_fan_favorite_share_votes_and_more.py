# Generated by Django 4.2.5 on 2024-04-18 21:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("survive", "0035_remove_tribe_season_tribe_season"),
    ]

    operations = [
        migrations.AddField(
            model_name="rubric",
            name="fan_favorite_share_votes",
            field=models.BooleanField(
                default=True,
                verbose_name="Whether fan favorite vote for this season includes all linked seasons' votes, or just its own",
            ),
        ),
        migrations.AlterField(
            model_name="rubric",
            name="fan_favorite",
            field=models.IntegerField(
                default=2,
                verbose_name="The points awarded to the fan favorite, optionally determined by a vote on this site.",
            ),
        ),
        migrations.AlterField(
            model_name="rubric",
            name="fan_favorite_negative_votes",
            field=models.BooleanField(
                default=True,
                verbose_name="Whether the fan favorite vote includes a 'bad' vote. True means the bad vote is present, False means it is not.",
            ),
        ),
        migrations.AlterField(
            model_name="rubric",
            name="fan_favorite_self_votes",
            field=models.BooleanField(
                default=False,
                verbose_name="Whether the fan favorite vote allows you to vote for survivors on your own team. True means you can self-vote, False means you cannot.",
            ),
        ),
        migrations.AlterField(
            model_name="rubric",
            name="finalist",
            field=models.IntegerField(
                default=2,
                verbose_name="The points awarded to the survivors who make it to the final jury, but don't win. The winner does not receive these points.",
            ),
        ),
        migrations.AlterField(
            model_name="rubric",
            name="idols",
            field=models.IntegerField(
                default=2,
                verbose_name="The points awarded to the survivor with the most immunity idols. Does not include other miscellaneous advantages.",
            ),
        ),
        migrations.AlterField(
            model_name="rubric",
            name="idols_tie_split",
            field=models.BooleanField(
                default=True,
                verbose_name="Whether ties in most idols split points. True means points are split, False means each survivor is rewarded the maximum value.",
            ),
        ),
        migrations.AlterField(
            model_name="rubric",
            name="immunities",
            field=models.IntegerField(
                default=2,
                verbose_name="The points awarded to the survivor who won the most immunity challenges.",
            ),
        ),
        migrations.AlterField(
            model_name="rubric",
            name="immunities_tie_split",
            field=models.BooleanField(
                default=True,
                verbose_name="Whether ties in most immunities split points. True means points are split, False means each survivor is rewarded the maximum value.",
            ),
        ),
        migrations.AlterField(
            model_name="rubric",
            name="jury_number",
            field=models.IntegerField(
                default=1,
                verbose_name="The points awarded based on when a survivor reached the jury. Survivors never eliminated will receive the highest jury number awarded in the season.         The first survivor to be a member of the jury receives this many points, & subsequent survivors receive a multiple of that.",
            ),
        ),
        migrations.AlterField(
            model_name="rubric",
            name="winner",
            field=models.IntegerField(
                default=5,
                verbose_name="The points awarded to the sole survivor of the season. This is awarded instead of Finalist points, not in addition to.",
            ),
        ),
    ]
