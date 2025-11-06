from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from .forms import EnrollCodeForm, CreateTeamForm, JoinTeamForm
from .models import Team, Profile

def enroll(request):
    if request.user.is_authenticated:
        return redirect("/")
    if request.method == "POST":
        form = EnrollCodeForm(request.POST)
        if form.is_valid():
            request.session["class_ok"] = True
            next_url = request.session.pop("after_enroll_next", "/accounts/login/")
            return redirect(next_url)
    else:
        form = EnrollCodeForm()
    return render(request, "accounts/enroll.html", {"form": form})

@login_required
def profile(request):
    prof, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, "accounts/profile.html", {"profile": prof})

@login_required
def team_create(request):
    prof = request.user.profile
    if request.method == "POST":
        form = CreateTeamForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.owner = request.user
            team.save()
            prof.team = team
            prof.save()
            messages.success(request, f"Team '{team.name}' created. Join code: {team.join_code}")
            return redirect("accounts:profile")
    else:
        form = CreateTeamForm()
    return render(request, "accounts/team_create.html", {"form": form})

@login_required
def team_join(request):
    prof = request.user.profile
    if request.method == "POST":
        form = JoinTeamForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["join_code"].strip()
            team = get_object_or_404(Team, join_code=code)
            prof.team = team
            prof.save()
            messages.success(request, f"Joined team '{team.name}'.")
            return redirect("accounts:profile")
    else:
        form = JoinTeamForm()
    return render(request, "accounts/team_join.html", {"form": form})
