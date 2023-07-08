from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Match, Round

User = get_user_model()

player_queryset = User.objects.order_by("email")

MAX_ROUNDS_COUNT = 5
MAX_NORMAL_SCORE = 11
MIN_MATCH_SCORE = 11


class MatchForm(forms.Form):
    date = forms.DateField(initial=timezone.now)
    round_count = forms.IntegerField(min_value=1, max_value=MAX_ROUNDS_COUNT)
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

    def clean(self):
        errors = []
        cleaned_data = super().clean()
        round_count = cleaned_data.get("round_count")

        if round_count < 1 or round_count > 5:
            errors.append("Rounds must be between 1 and 5")
            raise ValidationError(errors)

        if cleaned_data["player_1"] == cleaned_data["player_2"]:
            errors.append("Same player on both sides")

        if errors:
            raise ValidationError(errors)

        return cleaned_data

    def save(self):
        data = super().clean()
        match = Match(
            player_1=data["player_1"],
            player_2=data["player_2"],
            date=data["date"],
        )
        match.save()
        return match


class RoundForm(forms.Form):
    winner = forms.ModelChoiceField(queryset=player_queryset, label="Winner")
    score_loser = forms.IntegerField(min_value=0, max_value=100, label="Loser score")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            Field("winner", required=True),
            Field("score_loser", required=True),
        )
        self.helper.form_class = "form-horizontal"
        self.helper.label_class = "col-md-3"
        self.helper.field_class = "col-md-3"

    def save(self, match, round_number):
        data = super().clean()
        winner = data["winner"]
        if match.player_1 != winner and match.player_2 != winner:
            raise ValidationError("Player not in match")
        loser = match.player_2 if winner == match.player_1 else match.player_1
        score_loser = data["score_loser"]
        score_winner = 11 if score_loser < 10 else score_loser + 2
        round = Round(
            round_number=round_number,
            loser=loser,
            winner=winner,
            score_loser=score_loser,
            score_winner=score_winner,
            match=match,
        )
        round.save()
        return round
