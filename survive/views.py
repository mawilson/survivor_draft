from django.shortcuts import render
from django.shortcuts import redirect
from survive.forms import (
    FanFavoriteForm,
    PredictionForm,
    UserProfileForm,
    RegisterUserForm,
    TeamCreationForm,
    DraftEnabledForm,
)
from django.contrib.auth import authenticate, login
from survive.models import Team, Survivor, Season, Rubric, User
from django.shortcuts import get_object_or_404
from channels.layers import get_channel_layer  # type: ignore[import-untyped]
from asgiref.sync import async_to_sync
import re
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.


def season_selector_request(request):
    """Helper method to interact with cookies to get season ID & set seasons & season context"""
    """Returns a two element tuple: first the context dictionary with season & seasons set within it, second a new_season_id (None if not provided)"""
    season_id = request.COOKIES.get(
        "season_id"
    )  # if season id has been set before, get it & use it for context
    context = {"seasons": Season.objects.all().order_by("name")}
    try:
        if season_id:
            context["season"] = Season.objects.get(id=season_id)
        else:
            context["season"] = (
                Season.objects.first()
            )  # just use the first Season in the DB, if it exists
    except ObjectDoesNotExist:
        context["season"] = (
            Season.objects.first()
        )  # just use the first Season in the DB, if it exists

    new_season_id = None
    if request.method == "GET":
        new_season_id = request.GET.get("season_id")
        if (
            new_season_id
        ):  # if new_season_id is present, it was provided via the Season selector, update cookie for it & the context
            context["season"] = Season.objects.get(id=new_season_id)

    return context, new_season_id


def season_selector_response(response, new_season_id):
    """Helper function to interact with cookies to set season ID cookie if a new one has been provided"""
    if new_season_id:
        age = 30 * 60 * 24 * 365  # half of a year lifetime
        response.set_cookie("season_id", new_season_id, samesite="Lax", max_age=age)


def home(request):
    context, new_season_id = season_selector_request(request)
    team_creation_form = TeamCreationForm(
        request.POST or None, instance=Team(season=context["season"])
    )
    draft_enabled_form = DraftEnabledForm(
        request.POST or None, instance=context["season"]
    )

    if request.user.is_authenticated:
        context["team_associable"] = (
            len(request.user.team_set.filter(season_id=context["season"].id)) == 0
        )
        context["team_form"] = team_creation_form
        user_team = request.user.team_set.filter(
            season_id=context["season"].id
        ).first()  # user can have multiple teams - use the first from this season
        context["user_team"] = user_team
        context["draft_enabled_form"] = draft_enabled_form
    else:
        context["team_associable"] = False
        user_team = None  # an inauthenticated user has no teams

    user_team_id = (
        user_team.id if user_team else None
    )  # ternary to prevent trying to access None.id if user_team was not found
    if user_team_id is not None:
        context["user_team_id"] = user_team_id

    display_type = request.GET.get("display_type")
    if display_type == "tribe":
        context["display_type"] = "tribe"
    else:
        context["display_type"] = "default"

    if context["display_type"] != "tribe":
        context["linked_seasons"] = context["season"].linked_seasons.all()

        teams = context[
            "season"
        ].team_set.all()  # always show teams in the selected season
        context["undrafted_survivors"] = (
            context["season"]
            .survivor_set.exclude(
                team__season__in=[
                    context["season"].id
                ]  # show all survivors who don't have a team for this season
            )
            .order_by("name")
        )
        if context["season"].survivor_drafting:
            context["drafters"] = context["season"].draft_order()

        for linked_season in context[
            "linked_seasons"
        ]:  # always collect teams in linked seasons, though template may not display them
            teams = teams | linked_season.team_set.all()
        teams = sorted(teams, key=lambda t: t.name)  # first sort by name
        context["teams"] = sorted(
            teams, key=lambda t: t.points(), reverse=True
        )  # then sort by points, descending
    else:
        context["undrafted_survivors"] = (
            context["season"].survivor_set.filter(tribe=None).order_by("name")
        )

    if (
        request.method == "POST"
    ):  # there are a variety of types of POSTs that can come in to this view
        # use named hidden inputs submitted with the form to distinguish between them
        # the team_id variable is used to associate a user with a team, & also to select a team to draft a survivor to
        # survivor_id_draft is used to associate a survivor with a team, and survivor_id_undraft is used to disassociate a survivor with a team
        # if all of these are None, we are creating a team
        team_id = request.POST.get("team_id")
        survivor_id_draft = request.POST.get("survivor_id_draft")
        survivor_id_undraft = request.POST.get("survivor_id_undraft")
        draft_order = request.POST.get("draft_order")
        survivor_drafting = request.POST.get(
            "survivor_drafting"
        )  # used to toggle Season survivor_drafting
        survivor_drafting_helper = request.POST.get(
            "survivor_drafting_helper"
        )  # also used to help determine if it's a survivor_drafting POST
        if (
            draft_order is not None
        ):  # if draft_order was provided, it is a draft ordering post
            context["season"].reorder_draft(draft_order)
            return redirect("/")
        elif survivor_drafting_helper is not None:
            context["season"].survivor_drafting = (
                True if survivor_drafting == "on" else False
            )
            context["season"].save()
            return redirect("/")
        elif team_id is not None:  # team association requires the team_id field present
            team = get_object_or_404(Team, pk=request.POST.get("team_id"))
            if (
                team.user is None
            ):  # a Team should only be associable to a User if it does not already have one
                team.user = request.user
                team.save()
            return redirect("/")
        elif (
            survivor_id_draft is not None
        ):  # survivor drafting requires the survivor_id_draft field present
            team = get_object_or_404(Team, pk=user_team_id)
            survivor = get_object_or_404(Survivor, pk=survivor_id_draft)
            can_pick = team.can_pick()
            if not can_pick[0]:
                context["draft_out_of_order_error"] = can_pick[1]
                return render(request, "survive/home.html", context)
            if not survivor.team.filter(
                season__id=context["season"].id
            ):  # a Survivor should only be draftable by a Team if it currently does not have a Team for this Season
                survivor.team.add(team)
                survivor.save()
                num_drafted = len(
                    context[
                        "season"
                    ].survivor_set.filter(  # number of survivors in this season that have a team from this season
                        team__season__id=context["season"].id
                    )
                )
                draft_marker = context["season"].draft_marker
                if (
                    draft_marker >= 0
                ):  # negative values indicate draft order isn't being kept track of at all, leave it as such
                    new_draft_marker = num_drafted + 1
                    context["season"].draft_marker = new_draft_marker
                    context["season"].save()
                else:
                    new_draft_marker = draft_marker  # negative value stays put

                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "draft_" + str(context["season"].id),
                    {"type": "draft.message", "message": str(new_draft_marker)},
                )  # tell everyone in the season channel that the draft_marker has changed
            return redirect("/")
        elif (
            survivor_id_undraft is not None
        ):  # survivor undrafting requires the survivor_id_undraft field present
            team = get_object_or_404(
                Team, pk=user_team_id
            )  # still need to get to ensure only the owning Team can unclaim a Survivor
            survivor = get_object_or_404(Survivor, pk=survivor_id_undraft)
            survivor.team.remove(
                team
            )  # if Survivor Teams do not include team, this will fail silently, which is fine
            draft_marker = context["season"].draft_marker
            if draft_marker >= 0:
                new_draft_marker = 0
                context["season"].draft_marker = (
                    new_draft_marker  # set draft_marker to 0, a special state indicating somebody went & complicated the draft ordering
                )
                context["season"].save()
            else:
                new_draft_marker = draft_marker

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "draft_" + str(context["season"].id),
                {
                    "type": "draft.message",
                    "message": str(new_draft_marker),
                },  # draft_marker after an undraft is set to 0
            )  # tell everyone in the season channel that the draft_marker has changed
            return redirect("/")
        else:  # if POST did not include any POST variables, it is a POST to create a team
            if team_creation_form.is_valid():
                team_creation_form.instance.user = request.user
                if (
                    not team_creation_form.instance.captain
                ):  # if Captain was unprovided, fill one in
                    if not request.user.first_name:
                        team_creation_form.instance.captain = request.user.username
                    else:
                        team_creation_form.instance.captain = request.user.first_name
                team_creation_form.save()
                return redirect(
                    "/"
                )  # after submitting, redirect to home page to refresh
            else:
                return render(request, "survive/home.html", context)

    response = render(request, "survive/home.html", context)
    season_selector_response(response, new_season_id)
    return response


def survivor(request, **kwargs):
    id = kwargs["id"]
    team_id = kwargs["team_id"] if "team_id" in kwargs else None
    survivor = Survivor.objects.get(pk=id)
    context = {"survivor": survivor}
    season = request.COOKIES.get("season_id")
    if (
        team_id
    ):  # if team ID was provided (url is /survivor/survivor_id/team_id), then use that team & the season associated with it
        team = get_object_or_404(Team, pk=team_id)
        context["team"] = team
        context["season"] = team.season
    elif (
        season
    ):  # if team ID was not provided (url is just /survivor/survivor_id), then use the first team we can find associated with that survivor, & the cookie season
        season = get_object_or_404(Season, pk=season)
        context["season"] = season
        context["team"] = survivor.team.filter(
            season_id=season.id
        ).first()  # get first matching team for this survivor, for this season
    return render(request, "survive/survivor.html", context)


@login_required
def profile(request):
    if (
        request.user.is_authenticated
    ):  # process a POST to disassociate the profile from a team
        user_profile_form = UserProfileForm(request.POST or None, instance=request.user)
        context = {"form": user_profile_form}

        if request.method == "GET":
            edit_team_id = request.GET.get(
                "edit_team_id"
            )  # used to determine if we are editing a team
        else:
            edit_team_id = request.POST.get(
                "edit_team_id"
            )  # used to determine if we are editing a team
        if (
            edit_team_id is not None
        ):  # edit_team_id was provided, therefore we need to make a TeamCreationForm (whether for POST or GET)
            edit_team = get_object_or_404(Team, pk=edit_team_id)
            team_edit_form = TeamCreationForm(request.POST or None, instance=edit_team)

        if request.method == "POST":
            team_id = request.POST.get("team_id")
            team_id_delete = request.POST.get("team_id_delete")
            if (
                edit_team_id is not None
            ):  # edit_team_id was provided, therefore we are modifying a team
                if team_edit_form.is_valid():
                    edit_team.save()
                    return redirect("./")
                else:
                    return render(request, "survive/profile.html", context)
            elif team_id_delete is not None:
                Team.objects.filter(pk=team_id_delete).delete()
                return redirect(
                    "./"
                )  # after submitting, redirect to profile page to refresh
            elif (
                team_id is None
            ):  # team_id was not provided, therefore this is a profile field modification
                if user_profile_form.is_valid():
                    request.user.save()  # if done editing the profile, save changes to the user
                    return redirect("./")
                else:
                    context["edit"] = True  # rerender page in edit mode
                    return render(request, "survive/profile.html", context)
            else:  # team_id was provided, therefore this is a team disassociation action
                team = get_object_or_404(Team, pk=team_id)
                team.user = None
                team.save()
                return redirect(
                    "./"
                )  # after submitting, redirect to profile page to refresh
        else:
            if (
                request.GET.get("edit") == "True"
            ):  # if Edit was specified, render the page in edit mode
                context["edit"] = True
            else:  # else, render it as normal
                context["edit"] = False
            if (
                edit_team_id is not None
            ):  # if edit_team_id was specified, render the team with that ID in edit mode
                context["edit_team_id"] = int(edit_team_id)
                context["edit_team_form"] = team_edit_form
            return render(request, "survive/profile.html", context)
    else:
        return redirect("login")  # if not currently logged in, go to the login page


def fan_favorite(request):
    context, new_season_id = season_selector_request(request)

    if (
        request.user.is_authenticated
    ):  # if logged in, allow user to choose from teams that the User is associated with in that season
        teams = context["season"].team_set.filter(user_id=request.user.id)
        team = teams.first()
        context["form"] = FanFavoriteForm(request.POST or None, instance=team)
        context["team"] = team
    # if not logged in, cannot vote

    if request.method == "POST":
        form = context["form"]
        if form.is_valid():
            form.save(commit=True)
            team.season.fan_favorites(
                save=True
            )  # will evaluate all votes & assign Survivors accordingly
            return redirect("/")  # after submitting, return to home page
        else:
            context.update({"form": form})
            return render(request, "survive/fan_favorite_vote.html", context)
    else:
        response = render(request, "survive/fan_favorite_vote.html", context)
        season_selector_response(response, new_season_id)
        return response


def predictions(request):
    context, new_season_id = season_selector_request(request)

    if (
        request.user.is_authenticated
    ):  # if logged in, allow user to choose from teams that the User is associated with in that season
        teams = context["season"].team_set.filter(user_id=request.user.id)
        team = teams.first()
        context["form"] = PredictionForm(request.POST or None, instance=team)
        context["team"] = team
    # if not logged in, cannot predict

    if request.method == "POST":
        form = context["form"]
        if form.is_valid():
            form.save(commit=True)
            return redirect("/")  # after submitting, return to home page
        else:
            context.update({"form": form})
            return render(request, "survive/predictions.html", context)
    else:
        response = render(request, "survive/predictions.html", context)
        season_selector_response(response, new_season_id)
        return response


def register(request):
    form = RegisterUserForm(request.POST or None)
    context = {"form": form}

    if request.user.is_authenticated:
        return redirect("/")  # if already logged in, navigate to profile page instead
    elif request.method == "POST":
        if form.is_valid():
            # should log them in, then take them to profile
            new_user = form.save(commit=True)
            new_user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
            )
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
    context["seasons_using_rubric"] = ", ".join(
        sorted(season.name for season in seasons_using_rubric)
    )

    response = render(request, "survive/rubric.html", context)
    season_selector_response(response, new_season_id)
    return response


@staff_member_required  # should only be navigable from an admin page & with an admin user
def survivor_season_associate(request):
    if request.method == "GET":
        _survivors = request.GET["survivors"].split(",")
        survivors = []
        for survivor in _survivors:
            survivors.append(get_object_or_404(Survivor, pk=survivor))
        context = {
            "survivors": survivors,
            "seasons": Season.objects.all().order_by("name"),
        }
        return render(request, "survive/survivor_season_associate.html", context)
    else:
        season_ids = []
        survivors = []
        for key, value in request.POST.items():
            if re.match(r"seasons_selector_season_\d+", key):
                try:
                    season_id = int(value)
                except ValueError:
                    continue
                season_ids.append(season_id)
            elif re.match(r"survivor_\d+", key):
                try:
                    survivor_id = int(value)
                except ValueError:
                    continue
                survivors.append(get_object_or_404(Survivor, pk=survivor_id))

        for survivor in survivors:  # for each survivor
            for season in Season.objects.all():  # iterate through all existing seasons
                if (
                    season.id in season_ids
                ):  # add season to a survivor if it was found in the form (checkbox was checked)
                    survivor.season.add(
                        season
                    )  # succeeds even if season is already associated with survivor
                else:  # else remove season from the survivor
                    survivor.season.remove(
                        season
                    )  # succeeds even if season is not associated with survivor
            survivor.save()

        return redirect(
            reverse("admin:survive_survivor_changelist")
        )  # take us back to the Survivor admin page

@login_required # cannot create a season without being logged in
def create_season(request):
    context = {
        "seasons": Season.objects.all(),
        "rubrics": Rubric.objects.all() 
    }

    if request.method == "POST":
        season_id = request.POST.get("season_id")
        season_name = request.POST.get("season_name")
        rubric_id = request.POST.get("rubric_id")
        selected_rubric = get_object_or_404(Rubric, pk=rubric_id)
        selected_season = get_object_or_404(Season, pk=season_id)
        new_season = Season.objects.create(
            name = season_name,
            rubric = selected_rubric,
            team_creation = False
        )
        new_season.save()
        new_season.linked_seasons.add(selected_season)
        for survivor in selected_season.survivor_set.all(): # add new season to all survivors of selected_season
            survivor.season.add(new_season)
        for tribe in selected_season.tribe_set.all():
            tribe.season.add(new_season)

        new_team = Team.objects.create(
            season = new_season,
            captain = request.user.get_full_name(),
            user = request.user,
            name = f"{request.user.get_full_name()} Team",
            draft_owner = True # make creater of the season an admin
        )
        new_team.save()
        return redirect("manage_season")

    return render(request, "survive/create_season.html", context)

@login_required # cannot manage a season without being logged in
def manage_season(request):
    draft_owner_teams = request.user.team_set.filter(draft_owner=True)
    managed_seasons = []
    for team in draft_owner_teams: # in order to manage a season, a user's team must first be a draft owner of it
        if team.season.managed_season: # a managed season must also have the managed_season attribute set to True
            managed_seasons.append(team.season)
    
    context = {
        "managed_seasons": managed_seasons,
        "errors": [] # list of errors from POSTs
    }

    if request.method == "POST":
        invite_username = request.POST.get("user_invite")
        user_invite_season_id = request.POST.get("user_invite_season_id")
        delete_team_team_id = request.POST.get("delete_team_team_id")
        delete_season_season_id = request.POST.get("delete_season_season_id")

        if invite_username:
            try:
                user_to_invite = User.objects.get(username=invite_username)
            except User.DoesNotExist:
                context["errors"].append(f"Cannot invite user {invite_username}, user matching this username not found.")
                return render(request, "survive/manage_season.html", context)
            season = get_object_or_404(Season, pk=user_invite_season_id)

            for team in season.team_set.all():
                if team.user.username == invite_username:
                    context["errors"].append(f"Cannot invite user {invite_username} to season {season.name}, team '{team.name}' owned by this user is already present.")
                    return render(request, "survive/manage_season.html", context)
                
            if season not in managed_seasons:
                context["errors"].append(f"Cannot invite user {invite_username} to season {season.name}, your team is not a draft owner of this season, or this season is unmanaged.")
                return render(request, "survive/manage_season.html", context)
                
            user_full_name = user_to_invite.get_full_name()
            if user_full_name == "":
                team_prefix = user_to_invite.username
                new_team_name = user_to_invite.username + " Team"
            else:
                team_prefix = user_full_name
                new_team_name = user_full_name + " Team"
            new_team = Team(
                season = season,
                name = new_team_name,
                captain = team_prefix,
                user = user_to_invite
            )
            new_team.save()
        elif delete_team_team_id:
            team = get_object_or_404(Team, pk=delete_team_team_id)
            if team.season not in managed_seasons:
                context["errors"].append(f"Cannot delete team from season {team.season.name}, your team is not a draft owner of this season, or this season is unmanaged.")
                return render(request, "survive/manage_season.html", context)

            if team.season.team_set.filter(user__id=request.user.id) and len(team.season.team_set.filter(draft_owner=True)) <= 1:
                context["errors"].append(f"Cannot delete team {team.name} from season {team.season.name}, season manager can't remove their own team from a season without at least one other team that is a draft manager present.")
                return render(request, "survive/manage_season.html", context)

            team.delete()
        elif delete_season_season_id:
            season = get_object_or_404(Season, pk=delete_season_season_id)
            if season not in managed_seasons:
                context["errors"].append(f"Cannot delete season {season.name}, your team is not a draft owner of this season, or this season is unmanaged.")
                return render(request, "survive/manage_season.html", context)

            season.delete()
            return redirect("./")

    return render(request, "survive/manage_season.html", context)