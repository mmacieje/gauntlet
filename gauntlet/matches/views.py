import django.shortcuts as shortcuts
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView
from django.views.generic.detail import SingleObjectMixin

from .forms import DateForm, OpponentForm, RoundCountForm, RoundForm
from .models import Match, PlannedMatch, Tournament

User = get_user_model()

MAX_ROUNDS_PER_MATCH = 8
MAX_OWN_MATCHES = 10
MAX_OTHERS_MATCHES = 3


@login_required
def show_scores(request):
    others_matches = Match.objects.without_player(request.user).order_by("-date", "-pk")[:MAX_OTHERS_MATCHES]
    own_matches = Match.objects.with_player(request.user).order_by("-date", "-pk")[:MAX_OWN_MATCHES]
    matchsets = []
    matchsets.append({"name": "Last matches", "matches": others_matches})
    matchsets.append({"name": "Your matches", "matches": own_matches})
    return TemplateResponse(request, "matches/scores.html", {"matchsets": matchsets})


@login_required
def new_freeplay(request):
    if request.method == "POST":
        date_form = DateForm(request.POST, request.FILES)
        opponent_form = OpponentForm(request.POST, request.FILES, user=request.user)
        round_count_form = RoundCountForm(request.POST, request.FILES)
        rounds_formset = RoundForm.get_formset_factory()(request.POST, request.FILES, prefix="rounds")
        if (
            date_form.is_valid()
            and opponent_form.is_valid()
            and round_count_form.is_valid()
            and rounds_formset.is_valid()
        ):
            round_count = round_count_form.cleaned_data["round_count"]
            scores = rounds_formset.get_scores(round_count)
            match = Match(
                date=date_form.cleaned_data["date"],
                player_1=request.user,
                player_2=opponent_form.cleaned_data["opponent"],
                score_player_1=scores["player_1"],
                score_player_2=scores["player_2"],
                round_scores=scores["rounds"],
            )
            match.save()
            return shortcuts.redirect("matches:show_scores")
    else:
        date_form = DateForm()
        opponent_form = OpponentForm(user=request.user)
        round_count_form = RoundCountForm()
        rounds_formset = RoundForm.get_formset_factory()(prefix="rounds")

    return TemplateResponse(
        request,
        "matches/new_freeplay.html",
        {
            "date_form": date_form,
            "opponent_form": opponent_form,
            "round_count_form": round_count_form,
            "rounds_formset": rounds_formset,
        },
    )


@login_required
def new_planned(request, id):
    planned_match = shortcuts.get_object_or_404(PlannedMatch, id=id)
    if planned_match.actual_match is not None:
        # This planned match already has an outcome
        raise Http404

    if request.method == "POST":
        date_form = DateForm(request.POST, request.FILES)
        round_count_form = RoundCountForm(request.POST, request.FILES)
        rounds_formset = RoundForm.get_formset_factory()(request.POST, request.FILES, prefix="rounds")
        if date_form.is_valid() and round_count_form.is_valid() and rounds_formset.is_valid():
            round_count = round_count_form.cleaned_data["round_count"]
            scores = rounds_formset.get_scores(round_count, reverse=(request.user == planned_match.player_2))
            match = Match(
                date=date_form.cleaned_data["date"],
                player_1=planned_match.player_1,
                player_2=planned_match.player_2,
                score_player_1=scores["player_1"],
                score_player_2=scores["player_2"],
                round_scores=scores["rounds"],
            )
            match.save()
            planned_match.actual_match = match
            planned_match.save()
            return shortcuts.redirect("matches:tournament-detail", pk=planned_match.tournament.pk)
    else:
        date_form = DateForm()
        round_count_form = RoundCountForm()
        rounds_formset = RoundForm.get_formset_factory()(prefix="rounds")

    if request.user == planned_match.player_1:
        opponent = planned_match.player_2
    else:
        opponent = planned_match.player_1

    return TemplateResponse(
        request,
        "matches/new_tournament.html",
        {
            "date_form": date_form,
            "round_count_form": round_count_form,
            "rounds_formset": rounds_formset,
            "planned_match": planned_match,
            "opponent": opponent,
        },
    )


@method_decorator(login_required, name="dispatch")
class TournamentListView(ListView):
    queryset = Tournament.objects.order_by("-id")
    template_name = "matches/tournaments.html"


@method_decorator(login_required, name="dispatch")
class TournamentDetailView(SingleObjectMixin, View):
    model = Tournament
    template_name = "matches/tournament_details.html"

    def post(self, request, *args, **kwargs):
        tournament = self.get_object()
        user_in_tournament = request.user in tournament.players.all()

        if "withdraw" in request.POST and user_in_tournament:
            tournament.removePlayer(request.user)
        elif "sign_up" in request.POST and not user_in_tournament:
            tournament.addPlayer(request.user)
        # TODO this should be done via Admin interface instead
        elif "start" in request.POST and request.user.is_superuser:
            tournament.start()

        return self.details(request)

    def get(self, request, *args, **kwargs):
        return self.details(request)

    def details(self, request):
        tournament = self.get_object()

        if tournament.isInPlanning():
            return TemplateResponse(
                request,
                self.template_name,
                {"tournament": tournament},
            )

        scoreboard_df, leaderboard_df = tournament.get_boards()
        # TODO move styling out of backend code
        table_classes = "table table-striped table-bordered table-responsive"
        table_classes_rotated_header = table_classes + " vrt-header"
        scoreboard_html = scoreboard_df.to_html(classes=table_classes_rotated_header)
        leaderboard_html = leaderboard_df.to_html(classes=table_classes)
        matches_planned_for_user = tournament.planned_matches.with_player(request.user).not_played()
        return TemplateResponse(
            request,
            self.template_name,
            {
                "tournament": tournament,
                "matches_planned_for_user": matches_planned_for_user,
                "scoreboard_html": scoreboard_html,
                "leaderboard_html": leaderboard_html,
            },
        )
