from django.urls import path
from . import views

app_name = "docs"

urlpatterns = [
    path("", views.docs_index, name="index"),
    path("edit/", views.doc_edit, name="create"),
    path("edit/<slug:slug>/", views.doc_edit, name="edit"),
    path("<slug:slug>/", views.doc_view, name="view"),
]
