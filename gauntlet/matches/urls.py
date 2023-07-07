from django.urls import path

from gauntlet.matches.views import new, rounds_list

app_name = "matches"

urlpatterns = [
    path("scores/", rounds_list, name="scores"),
    path("new/", new, name="new"),
]
