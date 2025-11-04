from django.urls import path
from .views import diagram_list, diagram_create, diagram_detail

app_name = "diagrams"
urlpatterns = [
    path("", diagram_list, name="list"),
    path("new/", diagram_create, name="new"),
    path("<int:pk>/", diagram_detail, name="detail"),
]
