from django.contrib import admin
from .models import Policy

@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ("title","category","approved","version","updated_at")
    list_filter  = ("approved","category")
    search_fields = ("title","content","version")
    prepopulated_fields = {"slug": ("title",)}
