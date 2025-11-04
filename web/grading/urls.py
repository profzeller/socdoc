from django.urls import path
from .views import milestone_list, submit_work, view_scores, export_csv

app_name = "grading"
urlpatterns = [
    path("", milestone_list, name="list"),
    path("submit/", submit_work, name="submit"),
    path("scores/", view_scores, name="scores"),
    path("export.csv", export_csv, name="export"),
]
