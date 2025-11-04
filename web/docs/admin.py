from django.contrib import admin
from .models import DocPage

@admin.register(DocPage)
class DocAdmin(admin.ModelAdmin):
    list_display = ("title","author","approved","milestone","updated_at")
    list_filter = ("approved","milestone")
    search_fields = ("title","content")
    prepopulated_fields = {"slug": ("title",)}
