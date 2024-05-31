import itertools
from enum import Enum

import pandas as pd
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


# TODO just set the name of the user to the email sans domain and get rid of this helper
def get_user_name(user):
    return user.email.split("@")[0]


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

    def get_boards(self):
        played_matches = [p.actual_match for p in self.planned_matches.played()]
        player_names = [get_user_name(user) for user in self.players.all()]

        scoreboard = self.get_scoreboard(played_matches, player_names)
        leaderboard = self.get_leaderboard(played_matches, player_names)
        return scoreboard, leaderboard

    def get_leaderboard(self, played_matches, player_names):
        leaderboard = pd.DataFrame(0, player_names, ["Wins", "Matches", "Sets lost"])
        for match in played_matches:
            name_1 = get_user_name(match.player_1)
            name_2 = get_user_name(match.player_2)
            score_1 = match.score_player_1
            score_2 = match.score_player_2

            leaderboard.at[name_1, "Matches"] += 1
            leaderboard.at[name_2, "Matches"] += 1
            if score_1 > score_2:
                leaderboard.at[name_1, "Wins"] += 1
            elif score_2 > score_1:
                leaderboard.at[name_2, "Wins"] += 1
            for score in match.round_scores:
                if score[0] < score[1]:
                    leaderboard.at[name_1, "Sets lost"] += 1
                elif score[0] > score[1]:
                    leaderboard.at[name_2, "Sets lost"] += 1

        leaderboard.sort_values(by=["Wins", "Matches", "Sets lost"], inplace=True, ascending=[False, True, True])
        return leaderboard

    def get_scoreboard(self, played_matches, player_names):
        scoreboard = pd.DataFrame("-", player_names, player_names)
        for match in played_matches:
            name_1 = get_user_name(match.player_1)
            name_2 = get_user_name(match.player_2)
            score_1 = match.score_player_1
            score_2 = match.score_player_2

            scoreboard.at[name_2, name_1] = f"{score_2}:{score_1}"
            scoreboard.at[name_1, name_2] = f"{score_1}:{score_2}"
        return scoreboard

    def isInPlanning(self):
        return self.state == self.State.PLANNED.value

    def isOngoing(self):
        return self.state == self.State.ONGOING.value

    def isFinished(self):
        return self.state == self.State.FINISHED.value


class PlannedMatchQuerySet(MatchQuerySet):
    def played(self):
        return self.filter(~models.Q(actual_match=None))

    def not_played(self):
        return self.filter(actual_match=None)


class PlannedMatch(models.Model):
    player_1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="planned_match_player_1")
    player_2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="planned_match_player_2")
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, null=True, related_name="planned_matches")
    actual_match = models.ForeignKey(Match, on_delete=models.SET_NULL, null=True, blank=True)

    objects = PlannedMatchQuerySet.as_manager()

    class Meta:
        verbose_name_plural = "planned_matches"

    def __str__(self):
        s = f"PlannedMatch: {self.player_1}/{self.player_2}"
        return s
