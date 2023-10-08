from django.urls import path

from gauntlet.matches.views import new, scores, stats

app_name = "matches"

urlpatterns = [
    path("new/", new, name="new"),
    path("scores/", scores, name="scores"),
    path("stats/", stats, name="stats"),
]
