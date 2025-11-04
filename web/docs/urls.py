from django.urls import path
from .views import page_list, page_detail, page_create

app_name = "docs"
urlpatterns = [
    path("", page_list, name="list"),
    path("new/", page_create, name="new"),
    path("<slug:slug>/", page_detail, name="detail"),
]
