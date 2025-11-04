from django.urls import path
from .views import queue, approve_doc, approve_policy
app_name = "moderation"
urlpatterns = [
    path("", queue, name="queue"),
    path("approve/doc/<int:pk>/", approve_doc, name="approve_doc"),
    path("approve/policy/<int:pk>/", approve_policy, name="approve_policy"),
]
