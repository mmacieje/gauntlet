from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Match(models.Model):
    player_1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="match_player_1")
    player_2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="match_player_2")
    score_player_1 = models.PositiveSmallIntegerField(null=True)
    score_player_2 = models.PositiveSmallIntegerField(null=True)
    round_scores = models.JSONField(null=True)
    date = models.DateField(default=timezone.now)

    class Meta:
        verbose_name_plural = "matches"

    def __str__(self):
        s = f"Match: {self.player_1}/{self.player_2} "
        s += f"Score: {self.score_player_1}:{self.score_player_2}"
        return s


class Tournament(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, null=True, blank=True)
    players = models.ManyToManyField(User, blank=True)
