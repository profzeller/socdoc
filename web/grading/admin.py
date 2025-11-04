from django.contrib import admin
from .models import Milestone, Submission

@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ("title", "due_date", "max_points")

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("student", "milestone", "graded", "score", "submitted_at")
    list_filter = ("graded", "milestone")
    search_fields = ("student__username", "milestone__title")
