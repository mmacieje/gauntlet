from django.urls import path

from gauntlet.matches.views import new, scores

app_name = "matches"

urlpatterns = [
    path("scores/", scores, name="scores"),
    path("new/", new, name="new"),
]
