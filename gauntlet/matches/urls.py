from django.urls import path

from gauntlet.matches.views import TournamentDetailView, TournamentListView, new, new_planned, scores

app_name = "matches"

urlpatterns = [
    path("new/", new, name="new"),
    path("new/planned/<int:id>/", new_planned, name="new_planned"),
    path("scores/", scores, name="scores"),
    path("tournaments/", TournamentListView.as_view(), name="tournaments"),
    path("tournaments/<int:pk>/", TournamentDetailView.as_view(), name="tournament-detail"),
]
