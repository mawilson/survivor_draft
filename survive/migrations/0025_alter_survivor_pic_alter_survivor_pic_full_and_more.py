# Generated by Django 4.2.5 on 2024-02-02 05:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('survive', '0024_season_survivor_drafting'),
    ]

    operations = [
        migrations.AlterField(
            model_name='survivor',
            name='pic',
            field=models.ImageField(blank=True, default=None, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='survivor',
            name='pic_full',
            field=models.ImageField(blank=True, default=None, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='survivor',
            name='team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='survive.team', verbose_name='the team that recruited this survivor'),
        ),
        migrations.AlterField(
            model_name='survivor',
            name='tribe',
            field=models.CharField(blank=True, default=None, max_length=10, null=True),
        ),
    ]
