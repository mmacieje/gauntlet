from django.urls import path

from gauntlet.matches.views import new, scores, stats, tournament_details, tournaments

app_name = "matches"

urlpatterns = [
    path("new/", new, name="new"),
    path("scores/", scores, name="scores"),
    path("stats/", stats, name="stats"),
    path("tournaments/", tournaments, name="tournaments"),
    path("tournaments/<int:id>/", tournament_details, name="tournament_details"),
]
