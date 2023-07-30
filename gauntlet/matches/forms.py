from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Match

User = get_user_model()

player_queryset = User.objects.order_by("email")

MAX_ROUNDS_PER_MATCH = 10
MIN_ROUND_SCORE = 11


class MatchForm(forms.Form):
    date = forms.DateField(initial=timezone.now)
    round_count = forms.IntegerField(min_value=1, max_value=MAX_ROUNDS_PER_MATCH)
    player_1 = forms.ModelChoiceField(queryset=player_queryset, label="Player 1")
    player_2 = forms.ModelChoiceField(queryset=player_queryset, label="Player 2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.form_style = "inline"
        self.helper.form_class = "form-horizontal"
        self.helper.label_class = "col-sm-4 col-lg-2"
        self.helper.field_class = "col-sm-8 col-lg-4"
        self.helper.css_class = "border border-secondary rounded p-3 my-3 col-md-6"
        self.helper.layout = Layout(
            Field("date", required=True),
            Field("player_1", required=True),
            Field("player_2", required=True),
            Field("round_count", required=True),
        )
        self.initial["round_count"] = MAX_ROUNDS_PER_MATCH

    def clean(self):
        errors = []
        cleaned_data = super().clean()
        round_count = cleaned_data.get("round_count")

        if round_count < 1 or round_count > MAX_ROUNDS_PER_MATCH:
            errors.append(f"Rounds must be between 1 and {MAX_ROUNDS_PER_MATCH}")

        if cleaned_data["player_1"] == cleaned_data["player_2"]:
            errors.append("Same player on both sides")

        if errors:
            raise ValidationError(errors)

        return cleaned_data

    def save(self, score_player_1, score_player_2, round_scores):
        data = self.clean()
        if data["player_1"].email < data["player_2"].email:
            match = Match(
                player_1=data["player_1"],
                player_2=data["player_2"],
                score_player_1=score_player_1,
                score_player_2=score_player_2,
                round_scores=round_scores,
                date=data["date"],
            )
        else:
            match = Match(
                player_1=data["player_2"],
                player_2=data["player_1"],
                score_player_1=score_player_2,
                score_player_2=score_player_1,
                round_scores=[list(reversed(r)) for r in round_scores],
                date=data["date"],
            )
        match.save()
        return match


class RoundForm(forms.Form):
    winner = forms.ModelChoiceField(queryset=player_queryset, label="Winner")
    score_winner = forms.IntegerField(min_value=0, max_value=100, label="Winner score")
    score_loser = forms.IntegerField(min_value=0, max_value=100, label="Loser score")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            Field("winner", required=True),
            Field("score_loser", required=True),
            Field("score_winner", required=False, readonly=True),
        )
        self.helper.form_class = "form-horizontal"
        self.helper.label_class = "col-3"
        self.helper.field_class = "col-9"
        self.initial["score_winner"] = MIN_ROUND_SCORE
        self.initial["score_loser"] = 0

    def clean(self):
        errors = []
        cleaned_data = super().clean()
        score_loser = cleaned_data.get("score_loser")
        score_winner = cleaned_data.get("score_winner")

        if score_loser < 0 or score_winner < 0:
            errors.append("Scores cannot bo lower than 0")

        if score_loser > (score_winner - 2):
            errors.append("Winner must score at least 2 points more than the loser")

        if score_winner < MIN_ROUND_SCORE:
            errors.append(f"The winner must score at least {MIN_ROUND_SCORE} points")

        if errors:
            raise ValidationError(errors)

        return cleaned_data
