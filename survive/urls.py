from django.urls import path
from survive import views

urlpatterns = [
    path("", views.home, name="home"),
    path("add_team/", views.add_team, name="add_team")
]