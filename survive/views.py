from django.shortcuts import render
from django.shortcuts import redirect
from survive.forms import TeamForm, FanFavoriteForm
from survive.models import Team, Survivor, Season
from django.views.generic import ListView
from django.shortcuts import get_object_or_404

class HomeListView(ListView):
    """Renders the home page, with a list of all teams."""
    model = Team

    def get_context_data(self, **kwargs):
        context = super(HomeListView, self).get_context_data(**kwargs)
        return context

# Create your views here.

# def home(request):
#     return render(request, "survive/home.html")

def add_team(request):
    form = TeamForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            team = form.save(commit=True)
            return redirect("home")
    else:
        return render(request, "survive/add_team.html", {"form": form})
    
def survivor(request, id):
    context = {'survivor': Survivor.objects.get(pk=id)}
    return render(request, "survive/survivor.html", context)

def fan_favorite(request):
    context = {
        "form": FanFavoriteForm(request.POST or None),
        "teams": Team.objects.all(),
        "season": Season.objects.all()[0]
    }

    if request.method == "POST":     
        selected_team = get_object_or_404(Team, pk = request.POST.get("team_id"))
        form = FanFavoriteForm(context["form"].data, instance = selected_team) # can't change the existing form's instance, but can make a new one with identical data
        if form.is_valid():
            form.save(commit=True)
            selected_team.season.fan_favorites() # will evaluate all votes & assign Survivors accordingly
            return redirect("./") # after submitting, redirect to same page to refresh
        else:
            return render(request, "survive/fan_favorite_vote.html", {"form": form, "teams": context["teams"], "selected_team": selected_team.id, "season": context["season"]})
    else:
        return render(request, "survive/fan_favorite_vote.html", context)