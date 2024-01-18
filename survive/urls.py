from django.urls import path
from survive import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.home, name="home"),
    path("profile/", views.profile, name="profile"),
    path("survivor/<int:id>/", views.survivor, name="survivor_page"),
    path("fan_favorite/", views.fan_favorite, name="fan_favorite"),
    path("predictions/", views.predictions, name="predictions"),

    # account/auth paths
    path("accounts/login/", auth_views.LoginView.as_view(template_name="survive/login.html", redirect_authenticated_user=True), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
    path("accounts/password_change/", auth_views.PasswordChangeView.as_view(), name="password_change"),
    path("accounts/password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("accounts/password_reset_confirm/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("accounts/password_reset_done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("accounts/register/", views.register, name="register"),
]