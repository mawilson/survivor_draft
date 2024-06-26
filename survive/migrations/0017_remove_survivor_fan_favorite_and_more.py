# Generated by Django 4.2.5 on 2023-12-20 09:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("survive", "0016_team_fan_favorite_bad_team_fan_favorite_first_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="survivor",
            name="fan_favorite",
        ),
        migrations.AlterField(
            model_name="team",
            name="fan_favorite_bad",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="survive.survivor",
                verbose_name="Negative place fan favorite vote submitted by this team",
            ),
        ),
        migrations.AlterField(
            model_name="team",
            name="fan_favorite_first",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="survive.survivor",
                verbose_name="First place fan favorite vote submitted by this team",
            ),
        ),
        migrations.AlterField(
            model_name="team",
            name="fan_favorite_second",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="survive.survivor",
                verbose_name="Second place fan favorite vote submitted by this team",
            ),
        ),
        migrations.AlterField(
            model_name="team",
            name="fan_favorite_third",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="survive.survivor",
                verbose_name="Third place fan favorite vote submitted by this team",
            ),
        ),
    ]
