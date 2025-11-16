from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # Our account utilities (enroll, profile, team create/join)
    path("accounts/", include("accounts.urls")),

    # Allauth handles login/signup/logout + Discord
    path("accounts/", include("allauth.urls")),

    path("markdownx/", include("markdownx.urls")),
    path("docs/", include("docs.urls")),
    path("policies/", include("policies.urls")),
    path("diagrams/", include("diagrams.urls")),
    path("grading/", include("grading.urls")),
    path("moderation/", include("moderation.urls")),

    path("", TemplateView.as_view(template_name="home.html"), name="home"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)