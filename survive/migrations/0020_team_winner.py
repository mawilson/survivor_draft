# Generated by Django 4.2.5 on 2024-01-01 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survive', '0019_season_season_close'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='winner',
            field=models.BooleanField(default=False),
        ),
    ]
