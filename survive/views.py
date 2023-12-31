from django.shortcuts import render
from django.shortcuts import redirect
from survive.forms import FanFavoriteForm, PredictionForm
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

def season_selector_request(request):
    """Helper method to interact with cookies to get season ID & set seasons & season context"""
    """Returns a two element tuple: first the context dictionary with season & seasons set within it, second a new_season_id (None if not provided)"""
    season_id = request.COOKIES.get("season_id") # if season id has been set before, get it & use it for context
    context = {
        "seasons": Season.objects.all().order_by("name")
    }
    if season_id:
        context["season"] = Season.objects.get(id=season_id)
    else:
        context["season"] = Season.objects.first() # just use the first Season in the DB, if it exists

    new_season_id = None
    if request.method == "GET":
        new_season_id = request.GET.get("season_id")
        if new_season_id: # if new_season_id is present, it was provided via the Season selector, update cookie for it & the context
            context["season"] = Season.objects.get(id=new_season_id)

    return context, new_season_id

def season_selector_response(response, new_season_id):
    """Helper function to interact with cookies to set season ID cookie if a new one has been provided"""
    if new_season_id:
        response.set_cookie("season_id", new_season_id)

def home(request):
    context, new_season_id = season_selector_request(request)

    response = render(request, "survive/home.html", context)
    season_selector_response(response, new_season_id)
    return response
    
def survivor(request, id):
    context = {'survivor': Survivor.objects.get(pk=id)}
    return render(request, "survive/survivor.html", context)

def fan_favorite(request):
    context, new_season_id = season_selector_request(request)

    team = context["season"].team_set.first()
    initial_data = {"fan_favorite_first": None, "fan_favorite_second": None, "fan_favorite_third": None, "fan_favorite_bad": None}
    context["form"] = FanFavoriteForm(request.POST or None, instance = team, initial = initial_data)

    if request.method == "POST":     
        selected_team = get_object_or_404(Team, pk = request.POST.get("team_id"))
        form = FanFavoriteForm(context["form"].data, instance = selected_team) # can't change the existing form's instance, but can make a new one with identical data
        if form.is_valid():
            form.save(commit=True)
            selected_team.season.fan_favorites(save=True) # will evaluate all votes & assign Survivors accordingly
            return redirect("./") # after submitting, redirect to home page to refresh
        else:
            new_context = {
                "form": form,
                "selected_team": selected_team.id,
                "season": context["season"],
                "seasons": context["seasons"]
            }
            return render(request, "survive/fan_favorite_vote.html", new_context)
    else:
        response = render(request, "survive/fan_favorite_vote.html", context)
        season_selector_response(response, new_season_id)
        return response
    
def predictions(request):
    context, new_season_id = season_selector_request(request)
    
    team = context["season"].team_set.first()
    initial_data = {"prediction_first": None, "prediction_second": None, "prediction_third": None}
    context["form"] = PredictionForm(request.POST or None, instance = team, initial = initial_data)

    if request.method == "POST":     
        selected_team = get_object_or_404(Team, pk = request.POST.get("team_id"))
        form = PredictionForm(context["form"].data, instance = selected_team) # can't change the existing form's instance, but can make a new one with identical data
        if form.is_valid():
            form.save(commit=True)
            return redirect("./") # after submitting, redirect to home page to refresh
        else:
            new_context = {
                "form": form,
                "selected_team": selected_team.id,
                "season": context["season"],
                "seasons": context["seasons"]
            }
            return render(request, "survive/predictions.html", new_context)
    else:
        response = render(request, "survive/predictions.html", context)
        season_selector_response(response, new_season_id)
        return response