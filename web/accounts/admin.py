from django.contrib import admin
from .models import Team, Profile, ClassCode

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "join_code", "owner", "created_at")
    search_fields = ("name", "join_code")
    readonly_fields = ("join_code",)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "team", "discord_id")
    list_select_related = ("team", "user")
    search_fields = ("user__username", "user__email", "discord_id")

@admin.register(ClassCode)
class ClassCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "label", "active")
    list_filter = ("active",)
