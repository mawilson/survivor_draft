from django import forms
from survive.models import Team

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ("name", "captain",)