from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import ModelForm
from django.http import Http404
from .models import Policy

class PolicyForm(ModelForm):
    class Meta:
        model = Policy
        fields = ["category","title","slug","content","version"]

def policy_list(request):
    # published only
    policies = Policy.objects.filter(approved=True)
    # drafts owned by the current user (for visibility)
    drafts = []
    if request.user.is_authenticated:
        drafts = Policy.objects.filter(owner=request.user, approved=False).order_by("-updated_at")
    # group published by category for nicer display
    grouped = {}
    for p in policies:
        grouped.setdefault(p.get_category_display(), []).append(p)
    return render(request, "policies/list.html", {"grouped": grouped, "drafts": drafts})

def policy_detail(request, slug):
    p = get_object_or_404(Policy, slug=slug)
    if not p.approved:
        if not request.user.is_authenticated:
            raise Http404()
        if request.user != p.owner and not request.user.is_staff:
            raise Http404()
    return render(request, "policies/detail.html", {"policy": p})

@login_required
def policy_create(request):
    if request.method == "POST":
        form = PolicyForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.approved = False
            obj.save()
            return redirect("policies:list")
    else:
        form = PolicyForm()
    return render(request, "policies/edit.html", {"form": form})
