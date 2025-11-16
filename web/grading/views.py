from django import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Avg
from django.contrib import messages
from django.urls import reverse

import csv

from .models import Milestone, Submission, Evidence, Team  # grading models
from docs.models import DocPage


# ----- Forms -----


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ["milestone", "notes", "docs_url", "diagram", "policies"]


class EvidenceForm(forms.ModelForm):
    class Meta:
        model = Evidence
        fields = ["title", "link", "file"]


class DocSubmissionForm(forms.Form):
    """
    Simple form: choose which milestone this doc should count for.
    One submission per (milestone, student) is still enforced by the model.
    """
    milestone = forms.ModelChoiceField(
        queryset=Milestone.objects.all(),
        empty_label="Select a milestone",
        label="Milestone",
        help_text="Choose which milestone this documentation is for.",
    )


# ----- Views -----


@login_required
def milestone_list(request):
    """List milestones and indicate which ones the current user has submitted."""
    milestones = Milestone.objects.all().order_by("due_date")
    my_submissions = Submission.objects.filter(student=request.user)
    submitted_ids = {s.milestone_id for s in my_submissions}
    return render(
        request,
        "grading/list.html",
        {"milestones": milestones, "submitted_ids": submitted_ids},
    )


@login_required
def view_scores(request):
    """Show this student's scores."""
    subs = Submission.objects.select_related("milestone").filter(student=request.user)
    return render(request, "grading/scores.html", {"subs": subs})


@login_required
def submit_work(request):
    """
    Generic submission endpoint (not tied to a specific DocPage).
    Create/update a submission; optionally attach one piece of evidence per submit.
    """
    if request.method == "POST":
        sform = SubmissionForm(request.POST)
        eform = EvidenceForm(request.POST, request.FILES)
        if sform.is_valid():
            sub, created = Submission.objects.get_or_create(
                milestone=sform.cleaned_data["milestone"],
                student=request.user,
                defaults={
                    "notes": sform.cleaned_data.get("notes", ""),
                    "docs_url": sform.cleaned_data.get("docs_url", ""),
                    "diagram": sform.cleaned_data.get("diagram", ""),
                    "policies": sform.cleaned_data.get("policies", ""),
                },
            )
            if not created:
                sub.notes = sform.cleaned_data.get("notes", "")
                sub.docs_url = sform.cleaned_data.get("docs_url", "")
                sub.diagram = sform.cleaned_data.get("diagram", "")
                sub.policies = sform.cleaned_data.get("policies", "")
                sub.save()

            if eform.is_valid() and (eform.cleaned_data.get("link") or eform.cleaned_data.get("file")):
                ev = eform.save(commit=False)
                ev.submission = sub
                ev.save()

            # Try to auto-attach grading.Team if you’re still using that model
            if not sub.team:
                user_teams = request.user.teams.all()
                if user_teams.exists():
                    sub.team = user_teams.first()
                    sub.save()

            return redirect("grading:list")
    else:
        sform = SubmissionForm()
        eform = EvidenceForm()

    return render(request, "grading/submit.html", {"form": sform, "eform": eform})


@login_required
def export_csv(request):
    """Instructor-only: export all grades as CSV."""
    if not request.user.is_staff:
        return HttpResponse(status=403)

    resp = HttpResponse(content_type="text/csv")
    resp["Content-Disposition"] = "attachment; filename=grades.csv"
    w = csv.writer(resp)
    w.writerow(["username", "milestone", "score", "graded", "submitted_at"])

    for s in Submission.objects.select_related("student", "milestone"):
        w.writerow([s.student.username, s.milestone.title, s.score, s.graded, s.submitted_at])

    return resp


@staff_member_required
def team_matrix(request):
    teams = Team.objects.all().order_by("name")
    milestones = Milestone.objects.all().order_by("title")
    # average score per (team, milestone)
    grid = {}
    for t in teams:
        row = {}
        for m in milestones:
            avg = (
                Submission.objects
                .filter(team=t, milestone=m, graded=True)
                .aggregate(Avg("score"))["score__avg"]
            )
            row[m.id] = avg
        grid[t.id] = row
    return render(
        request,
        "grading/team_matrix.html",
        {"teams": teams, "milestones": milestones, "grid": grid},
    )


# ----- NEW: submit from a DocPage -----


@login_required
def submit_from_doc(request, slug):
    """
    Link a DocPage to a Milestone as a Submission for the current student.

    Rules:
    - Only members of the doc's team can submit it.
    - We DO NOT touch grading.Team membership here.
    - We store:
        - doc_page: FK to the page (for history)
        - docs_url: URL back to the doc, for graders to click through.
    """
    page = get_object_or_404(DocPage, slug=slug)

    # Must be team-based and user must be on that team (accounts.Profile.team)
    profile = getattr(request.user, "profile", None)
    if not profile or not profile.team:
        messages.error(request, "You must be on a team before submitting documentation.")
        return redirect("docs:detail", slug=page.slug)

    if not page.team or page.team != profile.team:
        messages.error(request, "You can only submit documentation for your own team’s pages.")
        return redirect("docs:detail", slug=page.slug)

    if request.method == "POST":
        form = DocSubmissionForm(request.POST)
        if form.is_valid():
            milestone = form.cleaned_data["milestone"]

            # Build an absolute URL to this doc
            doc_url = request.build_absolute_uri(
                reverse("docs:detail", args=[page.slug])
            )

            # 🔗 Create or update the student’s submission for this milestone,
            # and ensure it is tied to this specific DocPage.
            sub, created = Submission.objects.update_or_create(
                milestone=milestone,
                student=request.user,
                defaults={
                    "notes": "",
                    "docs_url": doc_url,
                    "diagram": "",
                    "policies": "",
                    "doc_page": page,
                },
            )

            messages.success(
                request,
                f"Submission saved for “{milestone.title}” using this doc."
            )
            return redirect("docs:detail", slug=page.slug)
    else:
        form = DocSubmissionForm()

    return render(
        request,
        "grading/submit_from_doc.html",
        {"page": page, "form": form},
    )
