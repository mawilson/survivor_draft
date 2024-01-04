from django import forms
from survive.models import Team, Season, Survivor

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ("name", "captain",)

class FanFavoriteForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ("fan_favorite_first", "fan_favorite_second", "fan_favorite_third", "fan_favorite_bad",)

    def __init__(self, *args, **kwargs):
        super(FanFavoriteForm, self).__init__(*args, **kwargs)
        if self.instance:
            season_id = self.instance.season.id if self.instance.season else None
            self.fields["fan_favorite_first"].queryset = Survivor.objects.filter(season__id=season_id)
            self.fields["fan_favorite_second"].queryset = Survivor.objects.filter(season__id=season_id)
            self.fields["fan_favorite_third"].queryset = Survivor.objects.filter(season__id=season_id)
            self.fields["fan_favorite_bad"].queryset = Survivor.objects.filter(season__id=season_id)

class PredictionForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ("prediction_first", "prediction_second", "prediction_third",)

    def __init__(self, *args, **kwargs):
        super(PredictionForm, self).__init__(*args, **kwargs)
        if self.instance:
            season_id = self.instance.season.id if self.instance.season else None
            self.fields["prediction_first"].queryset = Survivor.objects.filter(season__id=season_id)
            self.fields["prediction_second"].queryset = Survivor.objects.filter(season__id=season_id)
            self.fields["prediction_third"].queryset = Survivor.objects.filter(season__id=season_id)

class SeasonForm(forms.ModelForm):
    class Meta:
        model = Season
        fields = ("name",)