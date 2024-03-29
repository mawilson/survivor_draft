from django.shortcuts import render
from django.shortcuts import redirect
from survive.forms import FanFavoriteForm, PredictionForm, UserProfileForm, RegisterUserForm, TeamCreationForm, DraftEnabledForm
from django.contrib.auth import authenticate, login
from survive.models import Team, Survivor, Season
from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

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
        age = 30 * 60 * 24 * 365 # half of a year lifetime
        response.set_cookie("season_id", new_season_id, samesite="Lax", max_age=age)

def home(request):
    context, new_season_id = season_selector_request(request)
    team_creation_form = TeamCreationForm(request.POST or None, instance = Team(season = context["season"]))
    draft_enabled_form = DraftEnabledForm(request.POST or None, instance = context["season"])

    if (request.user.is_authenticated):
        context["team_associable"] = len(request.user.team_set.filter(season_id = context["season"].id)) == 0
        context["team_form"] = team_creation_form
        user_team = request.user.team_set.filter(season_id = context["season"].id).first() # user can have multiple teams - use the first from this season
        context["user_team"] = user_team
        context["draft_enabled_form"] = draft_enabled_form
    else:
        context["team_associable"] = False
        user_team = None # an inauthenticated user has no teams

    user_team_id = user_team.id if user_team else None # ternary to prevent trying to access None.id if user_team was not found
    if user_team_id is not None:
        context["user_team_id"] = user_team_id

    display_type = request.GET.get("display_type")
    if display_type == "tribe":
        context["display_type"] = "tribe"
    else:
        context["display_type"] = "default"

    if context["display_type"] != "tribe":
        context["linked_seasons"] = context["season"].linked_seasons.all()

        teams = context["season"].team_set.all() # always show teams in the selected season
        context["undrafted_survivors"] = context["season"].survivor_set.exclude(
            team__season__in=[context["season"].id] # show all survivors who don't have a team for this season
        ).order_by("name")
        if context["season"].survivor_drafting:
            context["drafters"] = context["season"].draft_order()

        for linked_season in context["linked_seasons"]: # always collect teams in linked seasons, though template may not display them
            teams = teams | linked_season.team_set.all()
        teams = sorted(teams, key = lambda t: t.name) # first sort by name
        context["teams"] = sorted(teams, key=lambda t: t.points(), reverse = True) # then sort by points, descending
    else:
        context["undrafted_survivors"] = context["season"].survivor_set.filter(tribe=None).order_by("name")

    if request.method == "POST": # there are a variety of types of POSTs that can come in to this view
        # use named hidden inputs submitted with the form to distinguish between them
        # the team_id variable is used to associate a user with a team, & also to select a team to draft a survivor to
        # survivor_id_draft is used to associate a survivor with a team, and survivor_id_undraft is used to disassociate a survivor with a team
        # if all of these are None, we are creating a team
        team_id = request.POST.get("team_id")
        survivor_id_draft = request.POST.get("survivor_id_draft")
        survivor_id_undraft = request.POST.get("survivor_id_undraft")
        draft_order = request.POST.get("draft_order")
        survivor_drafting = request.POST.get("survivor_drafting") # used to toggle Season survivor_drafting
        survivor_drafting_helper = request.POST.get("survivor_drafting_helper") # also used to help determine if it's a survivor_drafting POST
        if draft_order is not None: # if draft_order was provided, it is a draft ordering post
            context["season"].reorder_draft(draft_order)
            return redirect("/")
        elif survivor_drafting_helper is not None:
            context["season"].survivor_drafting = True if survivor_drafting == "on" else False
            context["season"].save()
            return redirect("/")
        elif team_id is not None: # team association requires the team_id field present
            team = get_object_or_404(Team, pk = request.POST.get("team_id"))
            if team.user is None: # a Team should only be associable to a User if it does not already have one
                team.user = request.user
                team.save()
            return redirect("/")
        elif survivor_id_draft is not None: # survivor drafting requires the survivor_id_draft field present
            team = get_object_or_404(Team, pk = user_team_id)
            survivor = get_object_or_404(Survivor, pk = survivor_id_draft)
            can_pick = team.can_pick()
            if not can_pick[0]:
                context["draft_out_of_order_error"] = can_pick[1]
                return render(request, "survive/home.html", context)
            if not survivor.team.filter(season__id=context["season"].id): # a Survivor should only be draftable by a Team if it currently does not have a Team for this Season
                survivor.team.add(team)
                survivor.save()
                num_drafted = len(context["season"].survivor_set.filter( # number of survivors in this season that have a team from this season
                    team__season__id=context["season"].id
                ))
                context["season"].draft_marker = num_drafted + 1
                context["season"].save()

                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "draft_" + str(context["season"].id), 
                    {"type": "draft.message", "message": str(num_drafted + 1)}
                ) # tell everyone in the season channel that the draft_marker has changed
            return redirect("/")  
        elif survivor_id_undraft is not None: # survivor undrafting requires the survivor_id_undraft field present
            team = get_object_or_404(Team, pk = user_team_id) # still need to get to ensure only the owning Team can unclaim a Survivor
            survivor = get_object_or_404(Survivor, pk = survivor_id_undraft)
            survivor.team.remove(team) # if Survivor Teams do not include team, this will fail silently, which is fine
            context["season"].draft_marker = 0 # set draft_marker to 0, a special state indicating somebody went & complicated the draft ordering
            context["season"].save()
            return redirect("/")
        else: # if POST did not include any POST variables, it is a POST to create a team
            if team_creation_form.is_valid():
                team_creation_form.instance.user = request.user
                if not team_creation_form.instance.captain: # if Captain was unprovided, fill one in
                    if not request.user.first_name:
                        team_creation_form.instance.captain = request.user.username
                    else:
                        team_creation_form.instance.captain = request.user.first_name
                team_creation_form.save()
                return redirect("/") # after submitting, redirect to home page to refresh
            else:
                return render(request, "survive/home.html", context)

    response = render(request, "survive/home.html", context)
    season_selector_response(response, new_season_id)
    return response
    
def survivor(request, **kwargs):
    id = kwargs["id"]
    team_id = kwargs["team_id"] if "team_id" in kwargs else None
    survivor = Survivor.objects.get(pk = id)
    context = {'survivor': survivor }
    season = request.COOKIES.get("season_id")
    if team_id: # if team ID was provided (url is /survivor/survivor_id/team_id), then use that team & the season associated with it
            team = get_object_or_404(Team, pk = team_id)
            context["team"] = team
            context["season"] = team.season
    elif season: # if team ID was not provided (url is just /survivor/survivor_id), then use the first team we can find associated with that survivor, & the cookie season
        season = get_object_or_404(Season, pk = season)
        context["season"] = season
        context["team"] = survivor.team.filter(season_id = season.id).first() # get first matching team for this survivor, for this season
    return render(request, "survive/survivor.html", context)

def profile(request):
    if request.user.is_authenticated: # process a POST to disassociate the profile from a team
        user_profile_form = UserProfileForm(request.POST or None, instance = request.user)
        context = {"form": user_profile_form}

        if request.method == "GET":
            edit_team_id = request.GET.get("edit_team_id") # used to determine if we are editing a team
        else:
            edit_team_id = request.POST.get("edit_team_id") # used to determine if we are editing a team
        if edit_team_id is not None: # edit_team_id was provided, therefore we need to make a TeamCreationForm (whether for POST or GET)
            edit_team = get_object_or_404(Team, pk = edit_team_id)
            team_edit_form = TeamCreationForm(request.POST or None, instance = edit_team)
        
        if request.method == "POST":
            team_id = request.POST.get("team_id")
            if edit_team_id is not None: # edit_team_id was provided, therefore we are modifying a team                
                if team_edit_form.is_valid():
                    edit_team.save()
                    return redirect("./")
                else:
                    return render(request, "survive/profile.html", context)
            elif team_id is None: # team_id was not provided, therefore this is a profile field modification
                if user_profile_form.is_valid():
                    request.user.save() # if done editing the profile, save changes to the user
                    return redirect("./")
                else:
                    context["edit"] = True # rerender page in edit mode
                    return render(request, "survive/profile.html", context)
            else: # team_id was provided, therefore this is a team disassociation action
                team = get_object_or_404(Team, pk = team_id)
                team.user = None
                team.save()
                return redirect("./") # after submitting, redirect to profile page to refresh   
        else:
            if request.GET.get("edit") == "True": # if Edit was specified, render the page in edit mode
                context["edit"] = True
            else: # else, render it as normal
                context["edit"] = False
            if edit_team_id is not None: # if edit_team_id was specified, render the team with that ID in edit mode
                context["edit_team_id"] = int(edit_team_id)
                context["edit_team_form"] = team_edit_form
            return render(request, "survive/profile.html", context)
    else:
        return redirect("login") # if not currently logged in, go to the login page

def fan_favorite(request):
    context, new_season_id = season_selector_request(request)

    if (request.user.is_authenticated): # if logged in, allow user to choose from teams that the User is associated with in that season
        teams = context["season"].team_set.filter(user_id=request.user.id)
        team = teams.first()
    else: # if not logged in, allow user the choose from the teams that do not have Users associated with them
        teams = context["season"].team_set.filter(user_id=None)
        team = teams.first()

    initial_data = {"fan_favorite_first": None, "fan_favorite_second": None, "fan_favorite_third": None, "fan_favorite_bad": None}
    context["form"] = FanFavoriteForm(request.POST or None, instance = team, initial = initial_data)
    context["teams"] = teams

    if request.method == "POST":     
        selected_team = get_object_or_404(Team, pk = request.POST.get("team_id"))
        form = FanFavoriteForm(context["form"].data, instance = selected_team) # can't change the existing form's instance, but can make a new one with identical data
        if form.is_valid():
            form.save(commit = True)
            selected_team.season.fan_favorites(save = True) # will evaluate all votes & assign Survivors accordingly
            return redirect("/") # after submitting, redirect to home page to refresh
        else:
            context.update({
                "form": form,
                "selected_team": selected_team.id,
                "season": context["season"],
                "seasons": context["seasons"],
                "teams": teams
            })
            return render(request, "survive/fan_favorite_vote.html", context)
    else:
        response = render(request, "survive/fan_favorite_vote.html", context)
        season_selector_response(response, new_season_id)
        return response
    
def predictions(request):
    context, new_season_id = season_selector_request(request)

    if (request.user.is_authenticated): # if logged in, allow user to choose from teams that the User is associated with in that season
        teams = context["season"].team_set.filter(user_id=request.user.id)
        team = teams.first()
    else: # if not logged in, allow user the choose from the teams that do not have Users associated with them
        teams = context["season"].team_set.filter(user_id=None)
        team = teams.first()
    
    initial_data = {"prediction_first": None, "prediction_second": None, "prediction_third": None}
    context["form"] = PredictionForm(request.POST or None, instance = team, initial = initial_data)
    context["teams"] = teams

    if request.method == "POST":     
        selected_team = get_object_or_404(Team, pk = request.POST.get("team_id"))
        form = PredictionForm(context["form"].data, instance = selected_team) # can't change the existing form's instance, but can make a new one with identical data
        if form.is_valid():
            form.save(commit = True)
            return redirect("/") # after submitting, redirect to home page to refresh
        else:
            context.update({
                "form": form,
                "selected_team": selected_team.id,
                "season": context["season"],
                "seasons": context["seasons"],
                "teams": teams
            })
            return render(request, "survive/predictions.html", context)
    else:
        response = render(request, "survive/predictions.html", context)
        season_selector_response(response, new_season_id)
        return response
    
def register(request):
    form = RegisterUserForm(request.POST or None)
    context = {"form": form }
    
    if request.user.is_authenticated:
        return redirect("/") # if already logged in, navigate to profile page instead
    elif request.method == "POST":  
        if form.is_valid():
            # should log them in, then take them to profile
            new_user = form.save(commit = True)
            new_user = authenticate(username = form.cleaned_data["username"], password = form.cleaned_data["password1"])
            login(request, new_user)
            return redirect("profile")
        else:
            return render(request, "survive/register.html", context)
    else:
        return render(request, "survive/register.html", context)
    
def rubric(request):
    context, new_season_id = season_selector_request(request)
    rubric = context["season"].rubric
    context["rubric"] = rubric
    seasons_using_rubric = rubric.season_set.all()
    context["seasons_using_rubric"] = ", ".join(sorted(season.name for season in seasons_using_rubric))

    response = render(request, "survive/rubric.html", context)
    season_selector_response(response, new_season_id)
    return response