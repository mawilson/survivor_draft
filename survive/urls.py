from django.urls import path
from survive import views
from survive.models import Team
from django.contrib.auth import views as auth_views

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
    path("fan_favorite", views.fan_favorite, name="fan_favorite"),
    path("predictions", views.predictions, name="predictions"),

    # account/auth paths
    path("accounts/login/", auth_views.LoginView.as_view(template_name="survive/login.html"), name="login"),
    #path("accounts/password_change/", auth_views.PasswordChangeView.as_view(template_name="survive/password_change.html"), name="password_change"),
    path("accounts/password_change/", auth_views.PasswordChangeView.as_view(), name="password_change"),
    path("accounts/password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("accounts/password_reset_confirm/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("accounts/password_reset_done", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
]