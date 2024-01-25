# Generated by Django 4.2.5 on 2024-01-25 00:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survive', '0022_team_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='captain',
            field=models.CharField(blank=True, max_length=300, verbose_name='Captain name'),
        ),
        migrations.AlterField(
            model_name='team',
            name='name',
            field=models.CharField(max_length=300, verbose_name='Team name'),
        ),
    ]
