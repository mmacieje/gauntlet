from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.forms import formset_factory
from django.shortcuts import redirect, render

from .forms import MatchForm, RoundForm
from .models import Match

User = get_user_model()


def rounds_list(request):
    matches = Match.objects.all().order_by("-pk")[:30]
    matches_data = []
    for match in matches:
        scores = [
            ["Match", match.score_player_1, match.score_player_2],
        ]
        round_count = 0
        for round_score in match.round_scores:
            round_count += 1
            print(round_score)
            scores.append([str(round_count), round_score[0], round_score[1]])
        match_data = {
            "player_1": match.player_1.email.split("@")[0],
            "player_2": match.player_2.email.split("@")[0],
            "date": match.date,
            "scores": scores,
        }
        matches_data.append(match_data)

    return render(request, "matches/scores.html", {"matches": matches_data})


class RoundFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_method = "post"
        self.render_required_fields = True
        self.add_input(Submit("submit", "Submit"))


MAX_SETS_PER_MATCH = 5


@login_required
def new(request):
    RoundFormset = formset_factory(RoundForm, extra=MAX_SETS_PER_MATCH)
    if request.method == "POST":
        match_form = MatchForm(request.POST, request.FILES, prefix="match")
        rounds_formset = RoundFormset(request.POST, request.FILES, prefix="rounds")

        if match_form.is_valid():
            rounds_valid = True
            for i in range(match_form.clean()["round_count"]):
                round = rounds_formset[i]
                if not round.is_valid():
                    rounds_valid = False
                    break
            if rounds_valid:
                match = match_form.clean()
                round_scores = []
                score_player_1 = 0
                score_player_2 = 0
                for i in range(match_form.clean()["round_count"]):
                    data = rounds_formset[i].clean()
                    winner = data["winner"]
                    if match["player_1"] != winner and match["player_2"] != winner:
                        raise ValidationError("Player not in match")
                    score_loser = data["score_loser"]
                    score_winner = 11 if score_loser < 10 else score_loser + 2
                    if winner == match["player_1"]:
                        score_player_1 += 1
                        round_score = [score_winner, score_loser]
                    else:
                        score_player_2 += 1
                        round_score = [score_loser, score_winner]
                    round_scores.append(round_score)
                match_form.save(score_player_1, score_player_2, round_scores)
                return redirect("matches:scores")
    else:
        match_form = MatchForm(prefix="match")
        rounds_formset = RoundFormset(prefix="rounds")
    return render(
        request,
        "matches/new.html",
        {"match_form": match_form, "rounds_formset": rounds_formset},
    )
