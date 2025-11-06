from django.urls import path
from . import views

app_name = "accounts"
urlpatterns = [
    path("enroll/", views.enroll, name="enroll"),
    path("profile/", views.profile, name="profile"),
    path("team/create/", views.team_create, name="team_create"),
    path("team/join/", views.team_join, name="team_join"),
]
