# Generated by Django 4.2.5 on 2024-10-03 05:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("survive", "0045_alter_season_rubric"),
    ]

    operations = [
        migrations.AddField(
            model_name="season",
            name="predictions_close",
            field=models.BooleanField(
                default=False,
                verbose_name="Predictions Close",
            ),
        ),
    ]