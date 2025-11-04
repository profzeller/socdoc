from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from accounts.views import SignUpView  # we'll add this view
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),  # allauth routes (login, logout, signup, social)
    path("markdownx/", include("markdownx.urls")),
    path("docs/", include("docs.urls")),
    path("policies/", include("policies.urls")),
    path("diagrams/", include("diagrams.urls")),
    path("grading/", include("grading.urls")),
    path("moderation/", include("moderation.urls")),
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
]
