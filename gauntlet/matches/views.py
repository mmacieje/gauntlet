from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from django.shortcuts import redirect, render

from .forms import MatchForm, RoundForm
from .models import MatchRound

User = get_user_model()


def rounds_list(request):
    match_rounds = MatchRound.objects.all().order_by("-pk")[:30]
    return render(request, "matches/scores.html", {"match_rounds": match_rounds})


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
        # TODO check for different sets of players between rounds

        if match_form.is_valid():
            rounds_valid = True
            for i in range(match_form.clean()["round_count"]):
                round = rounds_formset[i]
                if not round.is_valid():
                    rounds_valid = False
                    break
            if rounds_valid:
                match = match_form.save()
                for i in range(match_form.clean()["round_count"]):
                    round = rounds_formset[i]
                    round.save(match, i + 1)
                match.update()
                return redirect("matches:scores")
    else:
        match_form = MatchForm(prefix="match")
        rounds_formset = RoundFormset(prefix="rounds")
    return render(
        request,
        "matches/new.html",
        {"match_form": match_form, "rounds_formset": rounds_formset},
    )
