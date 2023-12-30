from django.urls import path
from survive import views
from survive.models import Team

home_list_view = views.HomeListView.as_view(
    queryset = Team.objects.order_by("name"), # alphabetic sort by Team Name, ascending
    context_object_name = "team_list",
    template_name = "survive/home.html",
)

urlpatterns = [
    path("", views.home, name="home"),
    #path("", home_list_view, name="home"),
    # path("add_team/", views.add_team, name="add_team") # deprecated
    path("survivor/<int:id>/", views.survivor, name="survivor_page"),
    path("fan_favorite", views.fan_favorite, name="fan_favorite")
]