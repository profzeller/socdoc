from django.contrib import admin
from .models import Milestone, Criterion, Submission, Evidence, CriterionScore

class CriterionInline(admin.TabularInline):
    model = Criterion
    extra = 1

@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ("title","due_date","max_points")
    inlines = [CriterionInline]

class EvidenceInline(admin.TabularInline):
    model = Evidence
    extra = 0

class CriterionScoreInline(admin.TabularInline):
    model = CriterionScore
    extra = 0

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("student","milestone","graded","score","submitted_at")
    list_filter = ("graded","milestone")
    search_fields = ("student__username","milestone__title")
    inlines = [EvidenceInline, CriterionScoreInline]
