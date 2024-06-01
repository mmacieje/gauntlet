from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Layout
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Match

User = get_user_model()

MAX_ROUNDS_PER_MATCH = 8
INITIAL_ROUNDS_PER_MATCH = 5
MIN_ROUND_SCORE = 11


class BasePartialForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.disable_csrf = True

        # TODO move styling out of backend code
        self.helper.form_style = "inline"
        self.helper.form_class = "form-horizontal"
        self.helper.label_class = "col-sm-4 col-lg-2"
        self.helper.field_class = "col-sm-8 col-lg-4"
        self.helper.css_class = "border border-secondary rounded p-3 my-3 col-md-6"


class DateForm(BasePartialForm):
    date = forms.DateField(initial=timezone.now, required=True)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("date") > timezone.now().date():
            raise ValidationError(["You cannot add a match played in the future"])
        return cleaned_data


class OpponentForm(BasePartialForm):
    opponent = forms.ModelChoiceField(queryset=User.objects.order_by("email"), required=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["opponent"].queryset = User.objects.order_by("email").exclude(id=self.user.id)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data["opponent"] == self.user:
            raise ValidationError(["You cannot play against yourself"])
        return cleaned_data


class RoundCountForm(BasePartialForm):
    round_count = forms.IntegerField(
        min_value=1, max_value=MAX_ROUNDS_PER_MATCH, required=False, initial=INITIAL_ROUNDS_PER_MATCH
    )

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


class BaseRoundFormSet(forms.BaseFormSet):
    # The returned scores assume player_1 is the active user,
    # unless reverse was set to True.
    def get_scores(self, round_count, reverse=False):
        def calculate_winner_score(loser_score):
            if loser_score < 10:
                return 11
            return loser_score + 2

        if any(self.errors):
            return
        scores = {
            "player_1": 0,
            "player_2": 0,
            "rounds": [],
        }
        print(round_count)
        for i in range(round_count):
            form = self.forms[i]
            score_loser = form.cleaned_data["score_loser"]
            player_1_won = form.cleaned_data["player_1_won"]
            if (player_1_won and not reverse) or (not player_1_won and reverse):
                scores["player_1"] += 1
                scores["rounds"].append([calculate_winner_score(score_loser), score_loser])
            else:
                scores["player_2"] += 1
                scores["rounds"].append([score_loser, calculate_winner_score(score_loser)])
        return scores


class RoundForm(forms.Form):
    player_1_won = forms.BooleanField(required=False)
    score_loser = forms.IntegerField(min_value=0, max_value=100, label="Loser score")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            Field("player_1_won", type="hidden"),
            Field("score_loser"),
        )
        self.helper.form_class = "form-horizontal"
        self.helper.label_class = "col-3"
        self.helper.field_class = "col-9"
        self.initial["player_1_won"] = "true"

    def get_formset_factory():
        # TODO this creates the max amount of round forms, which are then conditionally
        # hidden on the frontend. Rather, the frontend should dynamically create and delete
        # forms as necessary
        return forms.formset_factory(
            RoundForm,
            formset=BaseRoundFormSet,
            extra=MAX_ROUNDS_PER_MATCH,
            min_num=1,
            max_num=MAX_ROUNDS_PER_MATCH,
            absolute_max=MAX_ROUNDS_PER_MATCH,
            validate_min=True,
            validate_max=True,
        )
