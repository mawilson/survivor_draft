from django import forms
from survive.models import Team, Season

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ("name", "captain",)

class FanFavoriteForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ("fan_favorite_first", "fan_favorite_second", "fan_favorite_third", "fan_favorite_bad",)

class SeasonForm(forms.ModelForm):
    class Meta:
        model = Season
        fields = ("name",)