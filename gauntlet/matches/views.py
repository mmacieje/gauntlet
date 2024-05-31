import django.shortcuts as shortcuts
import plotly.express as px
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from django.http import Http404
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView
from django.views.generic.detail import SingleObjectMixin
from plotly.graph_objs import Bar
from plotly.offline import plot

from .forms import MatchForm, RoundForm, StatsForm
from .models import Match, PlannedMatch, Tournament

User = get_user_model()

MAX_ROUNDS_PER_MATCH = 8
MAX_OWN_MATCHES = 10
MAX_OTHERS_MATCHES = 3


@login_required
def scores(request):
    others_matches = Match.objects.without_player(request.user).order_by("-date", "-pk")[:MAX_OTHERS_MATCHES]
    own_matches = Match.objects.with_player(request.user).order_by("-date", "-pk")[:MAX_OWN_MATCHES]
    matchsets = []
    matchsets.append({"name": "Last matches", "matches": others_matches})
    matchsets.append({"name": "Your matches", "matches": own_matches})
    return TemplateResponse(request, "matches/scores.html", {"matchsets": matchsets})


@login_required
def new(request):
    return _new(request)


@login_required
def new_planned(request, id):
    planned = shortcuts.get_object_or_404(PlannedMatch, id=id)
    if planned.actual_match is not None:
        # This planned match already has an outcome
        raise Http404
    return _new(request, planned)


@login_required
def _new(request, planned=None):
    def render(request, match_form, rounds_formset, planned):
        return TemplateResponse(
            request,
            "matches/new.html",
            {"match_form": match_form, "rounds_formset": rounds_formset, "planned": planned},
        )

    def processScores(match_form, rounds_formset):
        round_scores = []
        score_player_1 = 0
        score_player_2 = 0
        for i in range(match_form.clean()["round_count"]):
            data = rounds_formset[i].clean()
            if data["player_1_is_the_winner"] == 1:
                score_player_1 += 1
                round_score = [data["score_winner"], data["score_loser"]]
            else:
                score_player_2 += 1
                round_score = [data["score_loser"], data["score_winner"]]
            round_scores.append(round_score)
        return {"round_scores": round_scores, "score_player_1": score_player_1, "score_player_2": score_player_2}

    RoundFormset = formset_factory(RoundForm, extra=MAX_ROUNDS_PER_MATCH)
    if request.method == "POST":
        match_form = MatchForm(request.POST, request.FILES, prefix="match")
        rounds_formset = RoundFormset(request.POST, request.FILES, prefix="rounds")

        if match_form.is_valid():
            match = match_form.clean()
            if (
                planned is None
                and match["player_1"] != request.user
                and match["player_2"] != request.user
                and not request.user.is_superuser
            ):
                match_form.add_error(None, "You can only register matches you played in yourself")
                return render(request, match_form, rounds_formset, planned)
            if planned is not None and (
                match["player_1"] != planned.player_1 or match["player_2"] != planned.player_2
            ):
                # TODO this is ugly, hide the form fields on frontend
                match_form.add_error(None, "Please don't change players on a planned match")
                return render(request, match_form, rounds_formset, planned)
            rounds_valid = True
            for i in range(match["round_count"]):
                round = rounds_formset[i]
                if not round.is_valid():
                    rounds_valid = False
                    break
            if rounds_valid:
                scores = processScores(match_form, rounds_formset)
                match = match_form.save(scores["score_player_1"], scores["score_player_2"], scores["round_scores"])
                if planned is not None:
                    planned.actual_match = match
                    planned.save()
                    return shortcuts.redirect("matches:tournament-detail", pk=planned.tournament.pk)
                else:
                    return shortcuts.redirect("matches:scores")
    else:
        if planned is not None:
            match_form = MatchForm(prefix="match", planned=planned)
        else:
            match_form = MatchForm(prefix="match", user=request.user)
        rounds_formset = RoundFormset(prefix="rounds", form_kwargs={"user": request.user})

    return render(request, match_form, rounds_formset, planned)


def calculate_results(matches, main_player):
    match_count = len(matches)
    if match_count == 0:
        return None
    results = {"match_count": match_count}

    match_stats = {
        "win_count": 0,
        "loose_count": 0,
        "draw_count": 0,
    }
    set_count = 0
    set_score_distribution = {}
    for i in list(range(-11, -1)) + list(range(2, 12)):
        set_score_distribution[int(i)] = 0
    for match in matches:
        if match.score_player_1 == match.score_player_2:
            match_stats["draw_count"] += 1
        elif (match.player_1 == main_player and match.score_player_1 > match.score_player_2) or (
            match.player_2 == main_player and match.score_player_2 > match.score_player_1
        ):
            match_stats["win_count"] += 1
        else:
            match_stats["loose_count"] += 1
        if match.round_scores is None:
            continue
        for round_score in match.round_scores:
            if match.player_1 == main_player:
                difference = round_score[0] - round_score[1]
            else:
                difference = round_score[1] - round_score[0]
            set_score_distribution[int(difference)] += 1
            set_count += 1
    normalized_distribution_keys = []
    normalized_distribution_vals = []
    for key, value in set_score_distribution.items():
        normalized_distribution_keys.append(key)
        normalized_distribution_vals.append(value / set_count * 100)
    results["match_stats"] = match_stats
    fig = Bar(x=normalized_distribution_keys, y=normalized_distribution_vals)
    fig = px.bar(x=normalized_distribution_keys, y=normalized_distribution_vals)
    fig.update_xaxes(range=[-11, 11])
    fig.update_layout(
        xaxis=dict(
            tickmode="array", tickvals=[-11, -8, -6, -4, -2, 2, 4, 6, 8, 11], title="Point difference in a sigle set"
        ),
        yaxis=dict(title="Percentage in all games"),
    )
    results["set_score_distribution_plot_div"] = plot(fig, output_type="div", include_plotlyjs=False)

    return results


@login_required
def stats(request):
    results = None
    if request.method == "POST":
        stats_form = StatsForm(request.POST, request.FILES)
        if stats_form.is_valid():
            matches = Match.objects.with_players(request.user, stats_form.cleaned_data["opponent"])
        results = calculate_results(matches, request.user)
    else:
        stats_form = StatsForm()

    return TemplateResponse(
        request,
        "matches/stats.html",
        {"stats_form": stats_form, "results": results},
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
