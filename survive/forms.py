from django import forms
from survive.models import Team, Season, Survivor, User, Rubric
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = (
            "name",
            "captain",
        )


class FanFavoriteForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = (
            "fan_favorite_first",
            "fan_favorite_second",
            "fan_favorite_third",
            "fan_favorite_bad",
        )

    def __init__(self, *args, **kwargs):
        super(FanFavoriteForm, self).__init__(*args, **kwargs)
        if self.instance:
            season_id = self.instance.season.id if self.instance.season else None
            self.fields["fan_favorite_first"].queryset = Survivor.objects.filter(
                season__id=season_id
            )
            self.fields["fan_favorite_second"].queryset = Survivor.objects.filter(
                season__id=season_id
            )
            self.fields["fan_favorite_third"].queryset = Survivor.objects.filter(
                season__id=season_id
            )
            self.fields["fan_favorite_bad"].queryset = Survivor.objects.filter(
                season__id=season_id
            )


class PredictionForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = (
            "prediction_first",
            "prediction_second",
            "prediction_third",
        )

    def __init__(self, *args, **kwargs):
        super(PredictionForm, self).__init__(*args, **kwargs)
        if self.instance:
            season_id = self.instance.season.id if self.instance.season else None
            self.fields["prediction_first"].queryset = Survivor.objects.filter(
                season__id=season_id,
                status=True
            )
            self.fields["prediction_second"].queryset = Survivor.objects.filter(
                season__id=season_id,
                status=True
            )
            self.fields["prediction_third"].queryset = Survivor.objects.filter(
                season__id=season_id,
                status=True
            )


class SeasonForm(forms.ModelForm):
    class Meta:
        model = Season
        fields = ("name",)


class RegisterUserForm(UserCreationForm):
    email = forms.EmailField(required=False)

    def __init__(self, *args, **kwargs):
        super(RegisterUserForm, self).__init__(*args, **kwargs)

        self.fields["username"].help_text = (
            "Username must be 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        )
        self.fields["password1"].help_text = (
            password_validation.password_validators_help_texts
        )  # had to dig this out to stop wrapping the items in <ul><li> tags
        self.fields["email"].help_text = (
            "Email is optional, but required for password resets. Can be added later after registration."
        )

    class Meta:
        model = User
        fields = ["email", "username", "password1", "password2"]

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        if (
            email != "" and User.objects.filter(email=email).exists()
        ):  # unique email check just in the Register form, no Models or DB checks
            self.add_error("email", "User with this Email address already exists.")
        return self.cleaned_data


class TeamCreationForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ("name", "captain")


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
        )


class DraftEnabledForm(forms.ModelForm):
    class Meta:
        model = Season
        fields = ("survivor_drafting",)
        widgets = {
            "survivor_drafting": forms.CheckboxInput(
                attrs={"onchange": "this.form.submit();", "name": "survivor_drafting"}
            )
        }


class RubricSelect(forms.Select):
    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):

        if isinstance(value, str):
            option = super().create_option(
                name, value, label, selected, index, subindex, attrs
            )
        else:
            option = super().create_option(
                name, value, value.instance.name, selected, index, subindex, attrs
            )

        return option


class SeasonManageForm(forms.ModelForm):
    class Meta:
        model = Season
        fields = (
            "rubric",
            "season_close",
            "season_open",
            "survivor_drafting",
            "team_creation",
            "predictions_close",
        )
        widgets = {
            "season_open": forms.TextInput(attrs={"placeholder": "2023-12-25"}),
            "season_close": forms.TextInput(attrs={"placeholder": "2023-12-26"}),
            "rubric": RubricSelect,
        }


class RubricCreateForm(forms.ModelForm):
    class Meta:
        model = Rubric
        fields = (
            "name",
            "idols",
            "idols_tie_split",
            "immunities",
            "immunities_tie_split",
            "confessionals",
            "confessionals_tie_split",
            "jury_number",
            "pity_point",
            "fan_favorite",
            "fan_favorite_self_votes",
            "fan_favorite_negative_votes",
            "fan_favorite_share_votes",
            "finalist",
            "winner",
        )
