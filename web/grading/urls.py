from django.urls import path
from .views import milestone_list, submit_work, view_scores, export_csv, team_matrix

app_name = "grading"
urlpatterns = [
    path("", milestone_list, name="list"),
    path("submit/", submit_work, name="submit"),
    path("scores/", view_scores, name="scores"),
    path("export.csv", export_csv, name="export"),
    path("teams/", team_matrix, name="teams"),
]
