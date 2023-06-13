from django.urls import path

from gauntlet.matches.views import new, rounds_list

app_name = "matches"

urlpatterns = [
    path("list-rounds/", rounds_list, name="match_rounds_list"),
    path("new/", new, name="new_match"),
]
