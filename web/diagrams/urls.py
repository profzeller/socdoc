# diagrams/urls.py
from django.urls import path
from .views import (
    diagram_list,
    diagram_create,
    diagram_detail,
    diagram_edit,
    diagram_publish,
)

app_name = "diagrams"

urlpatterns = [
    path("", diagram_list, name="list"),
    path("new/", diagram_create, name="create"),
    path("<int:pk>/", diagram_detail, name="detail"),
    path("<int:pk>/edit/", diagram_edit, name="edit"),
    path("<int:pk>/publish/", diagram_publish, name="publish"),
]
