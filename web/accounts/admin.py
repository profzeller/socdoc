from django.contrib import admin
from .models import Team, Profile, ClassCode, ClassConfig

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "member_count", "created_at")
    search_fields = ("name",)

    def member_count(self, obj):
        return obj.members.count()


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "team", "role_in_soc")
    list_filter = ("team",)
    search_fields = ("user__username", "display_name")

@admin.register(ClassConfig)
class ClassConfigAdmin(admin.ModelAdmin):
    list_display = ("students_can_create_teams",)

@admin.register(ClassCode)
class ClassCodeAdmin(admin.ModelAdmin):
    list_display = ("code", "label", "active")
    list_filter = ("active",)
