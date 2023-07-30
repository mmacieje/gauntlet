import django.shortcuts as shortcuts
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.forms import formset_factory

from .forms import MatchForm, RoundForm
from .models import Match

User = get_user_model()


@login_required
def scores(request):
    others_matches = Match.objects.filter(~Q(player_1=request.user) & ~Q(player_2=request.user)).order_by("-pk")[:3]
    own_matches = Match.objects.filter(Q(player_1=request.user) | Q(player_2=request.user)).order_by("-pk")[:30]
    matchsets = []
    matchsets.append({"name": "Last matches", "matches": others_matches})
    matchsets.append({"name": "Your matches", "matches": own_matches})
    return shortcuts.render(request, "matches/scores.html", {"matchsets": matchsets})


class RoundFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_method = "post"
        self.render_required_fields = True
        self.add_input(Submit("submit", "Submit"))


MAX_ROUNDS_PER_MATCH = 10


@login_required
def new(request):
    def render(request, match_form, rounds_formset):
        return shortcuts.render(
            request,
            "matches/new.html",
            {"match_form": match_form, "rounds_formset": rounds_formset},
        )

    RoundFormset = formset_factory(RoundForm, extra=MAX_ROUNDS_PER_MATCH)
    if request.method == "POST":
        match_form = MatchForm(request.POST, request.FILES, prefix="match")
        rounds_formset = RoundFormset(request.POST, request.FILES, prefix="rounds")

        if match_form.is_valid():
            match = match_form.clean()
            if (
                match["player_1"] != request.user
                and match["player_2"] != request.user
                and not request.user.is_superuser
            ):
                match_form.add_error(None, "You can only register matches you played in yourself")
                return render(request, match_form, rounds_formset)
            rounds_valid = True
            for i in range(match["round_count"]):
                round = rounds_formset[i]
                if not round.is_valid():
                    rounds_valid = False
                    break
            if rounds_valid:
                round_scores = []
                score_player_1 = 0
                score_player_2 = 0
                for i in range(match_form.clean()["round_count"]):
                    data = rounds_formset[i].clean()
                    winner = data["winner"]
                    if match["player_1"] != winner and match["player_2"] != winner:
                        match_form.add_error(None, "The winner is not a player on the match")
                        return render(request, match_form, rounds_formset)
                    if winner == match["player_1"]:
                        score_player_1 += 1
                        round_score = [data["score_winner"], data["score_loser"]]
                    else:
                        score_player_2 += 1
                        round_score = [data["score_loser"], data["score_winner"]]
                    round_scores.append(round_score)
                match_form.save(score_player_1, score_player_2, round_scores)
                return shortcuts.redirect("matches:scores")
    else:
        match_form = MatchForm(prefix="match")
        rounds_formset = RoundFormset(prefix="rounds")

    return render(request, match_form, rounds_formset)
