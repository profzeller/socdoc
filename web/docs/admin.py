from django.contrib import admin
from .models import DocPage, DocCategory


@admin.register(DocCategory)
class DocCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(DocPage)
class DocPageAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "team", "author", "updated_at")
    list_filter = ("category", "team", "author")
    search_fields = ("title", "body")
    prepopulated_fields = {"slug": ("title",)}
