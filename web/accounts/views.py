from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import EnrollCodeForm, CreateTeamForm, JoinTeamForm, ProfileForm
from .models import Team, Profile, ClassConfig


def enroll(request):
    """
    Gatekeeper using a class code before allowing registration/login.
    """
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        form = EnrollCodeForm(request.POST)
        if form.is_valid():
            # mark this browser as "class allowed"
            request.session["class_ok"] = True
            next_url = request.session.pop("after_enroll_next", "/accounts/login/")
            return redirect(next_url)
    else:
        form = EnrollCodeForm()

    return render(request, "accounts/enroll.html", {"form": form})


@login_required
def profile(request):
    """
    Show profile + team info.
    Optionally let the user edit display_name/role_in_soc.
    """
    prof, _ = Profile.objects.get_or_create(user=request.user)
    config = ClassConfig.get_solo()

    # Handle profile edits (display_name, role_in_soc)
    if request.method == "POST":
        pform = ProfileForm(request.POST, instance=prof)
        if pform.is_valid():
            pform.save()
            messages.success(request, "Profile updated.")
            return redirect("accounts:profile")
    else:
        pform = ProfileForm(instance=prof)

    # Team members to show when on a team
    team_members = None
    if prof.team:
        team_members = (
            Profile.objects.filter(team=prof.team)
            .select_related("user")
            .order_by("user__username")
        )

    return render(
        request,
        "accounts/profile.html",
        {
            "profile": prof,
            "team": prof.team,
            "team_members": team_members,
            "config": config,
            "profile_form": pform,
        },
    )


@login_required
def team_create(request):
    """
    Allow a student to create a team (if enabled), and automatically join it.
    """
    prof, _ = Profile.objects.get_or_create(user=request.user)
    config = ClassConfig.get_solo()

    # Respect the global toggle unless user is staff
    if not config.students_can_create_teams and not request.user.is_staff:
        messages.error(request, "Team creation by students is currently disabled.")
        return redirect("accounts:profile")

    # Don’t allow creating a second team if already on one
    if prof.team and not request.user.is_staff:
        messages.error(request, "You are already on a team.")
        return redirect("accounts:profile")

    if request.method == "POST":
        form = CreateTeamForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.owner = request.user
            team.save()
            prof.team = team
            prof.save()
            messages.success(
                request,
                f"Team '{team.name}' created. Share this join code with your teammates: {team.join_code}",
            )
            return redirect("accounts:profile")
    else:
        form = CreateTeamForm()

    return render(request, "accounts/team_create.html", {"form": form})


@login_required
def team_join(request):
    """
    Allow a student to join an existing team using its join_code.
    """
    prof, _ = Profile.objects.get_or_create(user=request.user)
    config = ClassConfig.get_solo()

    # Respect the global toggle unless staff is forcing a join
    if not config.students_can_create_teams and not request.user.is_staff:
        messages.error(request, "Self-joining teams is currently disabled.")
        return redirect("accounts:profile")

    # Already on a team? Don't allow casual switching.
    if prof.team and not request.user.is_staff:
        messages.error(request, "You are already on a team.")
        return redirect("accounts:profile")

    if request.method == "POST":
        form = JoinTeamForm(request.POST)
        if form.is_valid():
            # JoinTeamForm.clean_join_code already looked up the team
            team = form.team
            prof.team = team
            prof.save()
            messages.success(request, f"Joined team '{team.name}'.")
            return redirect("accounts:profile")
    else:
        form = JoinTeamForm()

    return render(request, "accounts/team_join.html", {"form": form})
