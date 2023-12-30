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

def home(request):
    season_id = request.COOKIES.get("season_id") # if season id has been set before, get it & use it for context
    context = {
        "seasons": Season.objects.all()
    }
    if season_id:
        context["season"] = Season.objects.get(id=season_id)
    else:
        context["season"] = Season.objects.all()[0] # just use the first Season in the DB, if it exists

    new_season_id = None
    if request.method == "GET":
        new_season_id = request.GET.get("season_id")
        if new_season_id: # if new_season_id is present, it was provided via the Season selector, update cookie for it & the context
            context["season"] = Season.objects.get(id=new_season_id)

    response = render(request, "survive/home.html", context)
    if new_season_id:
        response.set_cookie("season_id", new_season_id)
    return response
        


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
    season_id = request.COOKIES.get("season_id") # if season id has been set before, get it & use it for context
    context = {
        "form": FanFavoriteForm(request.POST or None),
        "seasons": Season.objects.all()
    }
    if season_id:
        context["season"] = Season.objects.get(id=season_id)
    else:
        context["season"] = Season.objects.all()[0] # just use the first Season in the DB, if it exists

    new_season_id = None
    if request.method == "GET":
        new_season_id = request.GET.get("season_id")
        if new_season_id: # if new_season_id is present, it was provided via the Season selector, update cookie for it & the context
            context["season"] = Season.objects.get(id=new_season_id)

    if request.method == "POST":     
        selected_team = get_object_or_404(Team, pk = request.POST.get("team_id"))
        form = FanFavoriteForm(context["form"].data, instance = selected_team) # can't change the existing form's instance, but can make a new one with identical data
        if form.is_valid():
            form.save(commit=True)
            selected_team.season.fan_favorites() # will evaluate all votes & assign Survivors accordingly
            return redirect("./") # after submitting, redirect to same page to refresh
        else:
            return render(request, "survive/fan_favorite_vote.html", {"form": form, "selected_team": selected_team.id, "season": context["season"]})
    else:
        response = render(request, "survive/fan_favorite_vote.html", context)
        if new_season_id:
            response.set_cookie("season_id", new_season_id)
        return response
