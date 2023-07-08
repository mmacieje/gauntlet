from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

User = get_user_model()


class Match(models.Model):
    player_1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="match_player_1")
    player_2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="match_player_2")
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="match_winner", null=True)
    score_player_1 = models.PositiveSmallIntegerField(null=True)
    score_player_2 = models.PositiveSmallIntegerField(null=True)
    date = models.DateField(default=timezone.now)

    class Meta:
        verbose_name_plural = "matches"

    def update(self):
        score_player_1 = 0
        score_player_2 = 0
        for round in self.round_set.all():
            if self.player_1 == round.winner:
                score_player_1 += 1
            elif self.player_2 == round.winner:
                score_player_2 += 1
            else:
                raise ValidationError("Got players not belonging to match")
        self.score_player_1 = score_player_1
        self.score_player_2 = score_player_2
        if score_player_1 > score_player_2:
            self.winner = self.player_1
        if score_player_1 < score_player_2:
            self.winner = self.player_2
        else:
            self.winner = None
        self.save()


class Round(models.Model):
    round_number = models.PositiveSmallIntegerField()
    loser = models.ForeignKey(User, on_delete=models.CASCADE, related_name="round_loser")
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="round_winner")
    score_loser = models.PositiveSmallIntegerField()
    score_winner = models.PositiveSmallIntegerField()

    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        s = f"Round: {self.round_number} {self.winner}/{self.loser} "
        s += "Score: {self.score_winner}:{self.score_loser}"
        return s
