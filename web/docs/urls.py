from django.urls import path
from . import views

app_name = "docs"

urlpatterns = [
    path("", views.docs_index, name="index"),
    path("new/", views.doc_create, name="create"),
    path("<slug:slug>/", views.doc_view, name="detail"),
    path("<slug:slug>/edit/", views.doc_edit, name="edit"),
    path("<slug:slug>/publish/", views.doc_publish, name="publish"),  # <-- NEW
]
