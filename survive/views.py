from django.shortcuts import render
from django.shortcuts import redirect
from survive.forms import TeamForm
from survive.models import Team

# Create your views here.

def home(request):
    return render(request, "survive/home.html")

def add_team(request):
    form = TeamForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            team = form.save(commit=True)
            return redirect("home")
    else:
        return render(request, "survive/add_team.html", {"form": form})