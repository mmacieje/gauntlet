import itertools
from enum import Enum

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class MatchQuerySet(models.QuerySet):
    def with_player(self, player):
        return self.filter(models.Q(player_1=player) | models.Q(player_2=player))

    def without_player(self, player):
        return self.filter(~models.Q(player_1=player) & ~models.Q(player_2=player))

    def with_players(self, player_1, player_2):
        return self.filter(
            models.Q(player_1=player_1, player_2=player_2) | models.Q(player_1=player_2, player_2=player_1)
        )


class Match(models.Model):
    player_1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="match_player_1")
    player_2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="match_player_2")
    score_player_1 = models.PositiveSmallIntegerField(null=True)
    score_player_2 = models.PositiveSmallIntegerField(null=True)
    round_scores = models.JSONField(null=True)
    date = models.DateField(default=timezone.now)

    objects = MatchQuerySet.as_manager()

    class Meta:
        verbose_name_plural = "matches"

    def __str__(self):
        s = f"Match: {self.player_1}/{self.player_2} "
        s += f"Score: {self.score_player_1}:{self.score_player_2}"
        return s

    def hasPlayer(self, user):
        return self.player_1 == user or self.player_2 == user


class Tournament(models.Model):
    class State(Enum):
        PLANNED = 1
        ONGOING = 2
        FINISHED = 3

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, null=True, blank=True)
    players = models.ManyToManyField(User, blank=True)
    state = models.SmallIntegerField(default=State.PLANNED.value)

    def removePlayer(self, player):
        if self.state != self.State.PLANNED.value:
            raise Exception("This tournament is not in the planning phase")
        if player not in self.players.all():
            raise Exception("Player already not signed up for this tournament")
        self.players.remove(player)
        self.save()

    def addPlayer(self, player):
        if self.state != self.State.PLANNED.value:
            raise Exception("This tournament is not in the planning phase")
        if player in self.players.all():
            raise Exception("Player already signed up for this tournament")
        self.players.add(player)
        self.save()

    def start(self):
        if self.state != self.State.PLANNED.value:
            raise Exception("This tournament is not in the planning phase")
        if self.players.count() < 2:
            raise Exception("Not enough players!")
        combinations = list(itertools.combinations(self.players.all(), 2))
        for player_pair in combinations:
            PlannedMatch.objects.create(player_1=player_pair[0], player_2=player_pair[1], tournament=self)
        self.state = self.State.ONGOING.value
        self.save()

    def isInPlanning(self):
        return self.state == self.State.PLANNED.value

    def isOngoing(self):
        return self.state == self.State.ONGOING.value

    def isFinished(self):
        return self.state == self.State.FINISHED.value


class PlannedMatch(models.Model):
    player_1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="planned_match_player_1")
    player_2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="planned_match_player_2")
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, null=True)
    actual_match = models.ForeignKey(Match, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name_plural = "planned_matches"

    def __str__(self):
        s = f"PlannedMatch: {self.player_1}/{self.player_2}"
        return s

    def hasPlayer(self, user):
        return self.player_1 == user or self.player_2 == user
