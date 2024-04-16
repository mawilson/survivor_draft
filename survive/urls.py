from django.urls import path
from survive import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.home, name="home"),
    path("profile/", views.profile, name="profile"),
    path("survivor/<int:id>/", views.survivor, name="survivor_page"),
    path("survivor/<int:id>/<int:team_id>/", views.survivor, name="survivor_page"),
    path("fan_favorite/", views.fan_favorite, name="fan_favorite"),
    path("predictions/", views.predictions, name="predictions"),
    path("rubric/", views.rubric, name="rubric"),
    
    # admin paths
    path("admin/survivor_season_associate", views.survivor_season_associate, name="survivor_season_associate"),

    # account/auth paths
    path("accounts/login/", auth_views.LoginView.as_view(template_name="survive/login.html", redirect_authenticated_user=True), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
    path("accounts/password_change/", auth_views.PasswordChangeView.as_view(template_name="survive/password_change.html"), name="password_change"),
    path("accounts/password_change_done/", auth_views.PasswordChangeDoneView.as_view(template_name="survive/password_change_done.html"), name="password_change_done"),
    path("accounts/password_reset/", auth_views.PasswordResetView.as_view(template_name="survive/password_reset.html", success_url="/accounts/password_reset_sent"), name="password_reset"),
    path("accounts/password_reset_confirm/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="survive/password_reset_confirm.html"), name="password_reset_confirm"),
    path("accounts/password_reset_sent/", auth_views.PasswordResetDoneView.as_view(template_name="survive/password_reset_sent.html"), name="password_reset_sent"),
    path("accounts/password_reset_complete/", auth_views.PasswordResetCompleteView.as_view(template_name="survive/password_reset_complete.html"), name="password_reset_complete"),
    path("accounts/register/", views.register, name="register"),
]