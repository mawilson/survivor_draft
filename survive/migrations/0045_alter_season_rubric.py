# Generated by Django 4.2.5 on 2024-05-10 21:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("survive", "0044_rubric_name_alter_rubric_confessionals_tie_split_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="season",
            name="rubric",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="survive.rubric",
                verbose_name="Rubric",
            ),
        ),
    ]