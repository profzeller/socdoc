from django.urls import path
from . import views

app_name = "policies"

urlpatterns = [
    path("", views.policy_list, name="list"),
    path("new/", views.policy_create, name="create"),
    path("<slug:slug>/", views.policy_detail, name="detail"),
    path("<slug:slug>/edit/", views.policy_edit, name="edit"),
    path("<slug:slug>/publish/", views.policy_publish, name="publish"),
]
