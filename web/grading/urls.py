from django.urls import path
from .views import (
    milestone_list,
    submit_work,
    view_scores,
    export_csv,
    team_matrix,
    submit_from_doc,
    milestone_submissions,   # NEW
    grade_submission,        # NEW
)

app_name = "grading"

urlpatterns = [
    path("", milestone_list, name="list"),
    path("submit/", submit_work, name="submit"),
    path("scores/", view_scores, name="scores"),
    path("export.csv", export_csv, name="export"),
    path("teams/", team_matrix, name="teams"),

    # submit a DocPage for a milestone
    path("submit-from-doc/<slug:slug>/", submit_from_doc, name="submit_from_doc"),

    # NEW: instructor grading screens
    path(
        "milestone/<int:pk>/submissions/",
        milestone_submissions,
        name="milestone_submissions",
    ),
    path(
        "submission/<int:pk>/grade/",
        grade_submission,
        name="grade_submission",
    ),
]
