# Generated by Django 4.2.5 on 2023-11-17 22:11

from django.db import migrations, models
import django.db.models.deletion
import survive.models


class Migration(migrations.Migration):

    dependencies = [
        ('survive', '0008_rubric_idols_tie_split_rubric_immunities_tie_split'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rubric',
            name='season',
        ),
        migrations.AddField(
            model_name='season',
            name='rubric',
            field=models.ForeignKey(default=survive.models.Rubric.get_default_pk, on_delete=django.db.models.deletion.CASCADE, to='survive.rubric'),
        ),
    ]
