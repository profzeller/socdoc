from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("markdownx/", include("markdownx.urls")),
    path("docs/", include("docs.urls")),
    path("policies/", include("policies.urls")),   # ← add
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
]
