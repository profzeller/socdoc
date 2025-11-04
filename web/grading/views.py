from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm
from .models import Milestone, Submission

class SubmissionForm(ModelForm):
    class Meta:
        model = Submission
        fields = ["milestone", "notes", "docs_url", "diagram", "policies"]

@login_required
def milestone_list(request):
    milestones = Milestone.objects.all().order_by("due_date")
    my_submissions = Submission.objects.filter(student=request.user)
    submitted_ids = [s.milestone_id for s in my_submissions]
    return render(request, "grading/list.html", {
        "milestones": milestones,
        "submitted_ids": submitted_ids
    })

@login_required
def submit_work(request):
    if request.method == "POST":
        form = SubmissionForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.student = request.user
            obj.save()
            return redirect("grading:list")
    else:
        form = SubmissionForm()
    return render(request, "grading/submit.html", {"form": form})

@login_required
def view_scores(request):
    subs = Submission.objects.filter(student=request.user)
    return render(request, "grading/scores.html", {"subs": subs})
