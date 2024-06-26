# Generated by Django 4.2.5 on 2023-11-13 23:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("survive", "0002_survivor_status"),
    ]

    operations = [
        migrations.CreateModel(
            name="Rubric",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("idolsWinner", models.IntegerField(default=1)),
                ("juryNumber", models.IntegerField(default=0)),
                ("fanFavorite", models.IntegerField(default=0)),
                ("winner", models.IntegerField(default=3)),
            ],
        ),
        migrations.AddField(
            model_name="survivor",
            name="advantages",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="survivor",
            name="confessionals",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="survivor",
            name="idols",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="survivor",
            name="juryNumber",
            field=models.IntegerField(default=0),
        ),
    ]
