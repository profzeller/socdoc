# diagrams/urls.py
from django.urls import path
from . import views

app_name = "diagrams"

urlpatterns = [
    path("", views.diagram_list, name="list"),
    path("new/", views.diagram_create, name="create"),
    path("<slug:slug>/", views.diagram_detail, name="detail"),
    path("<slug:slug>/edit/", views.diagram_edit, name="edit"),
    path("<slug:slug>/publish/", views.diagram_publish, name="publish"),
]
