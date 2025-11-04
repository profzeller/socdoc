from django.urls import path
from .views import policy_list, policy_detail, policy_create

app_name = "policies"
urlpatterns = [
    path("", policy_list, name="list"),
    path("new/", policy_create, name="new"),
    path("<slug:slug>/", policy_detail, name="detail"),
]
