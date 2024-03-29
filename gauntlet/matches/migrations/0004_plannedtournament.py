# Generated by Django 4.1.9 on 2023-11-01 12:53

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("matches", "0003_remove_match_winner_match_round_scores_delete_round"),
    ]

    operations = [
        migrations.CreateModel(
            name="PlannedTournament",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("players", models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
