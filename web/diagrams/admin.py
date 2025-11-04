from django.contrib import admin
from .models import Diagram

@admin.register(Diagram)
class DiagramAdmin(admin.ModelAdmin):
    list_display = ("title","owner","created_at")
    search_fields = ("title","notes","fossflow_url","owner__username")
