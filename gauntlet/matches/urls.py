from django.urls import path

from gauntlet.matches.views import TournamentDetailView, TournamentListView, new_freeplay, new_planned, show_scores

app_name = "matches"

urlpatterns = [
    path("new/freeplay/", new_freeplay, name="new_freeplay"),
    path("new/planned/<int:id>/", new_planned, name="new_planned"),
    path("scores/", show_scores, name="show_scores"),
    path("tournaments/", TournamentListView.as_view(), name="tournaments"),
    path("tournaments/<int:pk>/", TournamentDetailView.as_view(), name="tournament-detail"),
]
