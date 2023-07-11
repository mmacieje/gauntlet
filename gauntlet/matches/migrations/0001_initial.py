# Generated by Django 4.1.9 on 2023-07-07 20:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Match",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("score_player_1", models.PositiveSmallIntegerField(null=True)),
                ("score_player_2", models.PositiveSmallIntegerField(null=True)),
                ("date", models.DateField(default=django.utils.timezone.now)),
                (
                    "player_1",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="match_player_1",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "player_2",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="match_player_2",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "winner",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="match_winner",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "matches",
            },
        ),
        migrations.CreateModel(
            name="MatchRound",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("round_number", models.PositiveSmallIntegerField()),
                ("score_loser", models.PositiveSmallIntegerField()),
                ("score_winner", models.PositiveSmallIntegerField()),
                (
                    "loser",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="round_loser",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("match", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="matches.match")),
                (
                    "winner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="round_winner",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]