from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import ModelForm
from django.http import Http404
from django.contrib import messages

from .models import Policy


# -------------------------
# Helpers
# -------------------------

def get_user_team(user):
    """Return the accounts.Team for this user, or None."""
    prof = getattr(user, "profile", None)
    return getattr(prof, "team", None) if prof else None


def can_view_policy(user, policy: Policy) -> bool:
    """
    Centralized permission check for viewing a policy.

    Rules:
    - Approved + visibility in {"class", "global"} -> anyone can view (even anonymous).
    - Team-only or unapproved -> owner, team members, or staff.
    """
    # Staff can always see everything
    if user.is_authenticated and user.is_staff:
        return True

    # Unapproved drafts
    if not policy.approved:
        if not user.is_authenticated:
            return False
        if user == policy.owner:
            return True
        user_team = get_user_team(user)
        if policy.team and user_team == policy.team:
            return True
        return False

    # Approved: handle by visibility
    if policy.visibility in ("class", "global"):
        # class/global are visible to everyone (logged in or not)
        return True

    # team-only visibility
    if policy.visibility == "team":
        if not user.is_authenticated:
            return False
        if user == policy.owner:
            return True
        user_team = get_user_team(user)
        if policy.team and user_team == policy.team:
            return True
        return False

    # Fallback (shouldn't hit)
    return False


def can_edit_policy(user, policy: Policy) -> bool:
    """
    Who can edit a policy?
    - staff
    - owner
    - any member of the policy's team
    """
    if not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    if user == policy.owner:
        return True
    user_team = get_user_team(user)
    if policy.team and user_team == policy.team:
        return True
    return False


# -------------------------
# Forms
# -------------------------

class PolicyForm(ModelForm):
    class Meta:
        model = Policy
        # Note: no slug field here; slug is auto-generated from title in the model
        fields = ["category", "title", "content", "version"]


# -------------------------
# Views
# -------------------------

def policy_list(request):
    """
    Show:
      - Approved class/global policies for everyone.
      - Team drafts (unapproved or team-only) for the current user's team.
    """

    # Approved, visible-to-class/global policies
    published = Policy.objects.filter(
        approved=True,
        visibility__in=["class", "global"],
    ).order_by("category", "title")

    # Group published by category display name for nicer UI
    grouped = {}
    for p in published:
        grouped.setdefault(p.get_category_display(), []).append(p)

    # Team drafts if logged in + on a team
    team_drafts = []
    if request.user.is_authenticated:
        user_team = get_user_team(request.user)
        if user_team:
            team_drafts = (
                Policy.objects.filter(team=user_team)
                .exclude(approved=True, visibility__in=["class", "global"])
                .order_by("-updated_at")
            )

    return render(
        request,
        "policies/list.html",
        {
            "grouped": grouped,        # { "Incident Response": [policies…], ... }
            "team_drafts": team_drafts # drafts for this user's team
        },
    )


def policy_detail(request, slug):
    policy = get_object_or_404(Policy, slug=slug)

    if not can_view_policy(request.user, policy):
        raise Http404("Policy not found")

    # Can this user edit?
    can_edit = can_edit_policy(request.user, policy)

    # Can this user publish to class?
    can_publish = False
    if request.user.is_authenticated:
        if request.user.is_staff:
            can_publish = True
        else:
            user_team = get_user_team(request.user)
            if policy.team and user_team == policy.team:
                can_publish = True

    return render(
        request,
        "policies/detail.html",
        {
            "policy": policy,
            "can_edit": can_edit,
            "can_publish": can_publish,
        },
    )



@login_required
def policy_create(request):
    """
    Create a new team policy as a draft.

    - Owner = current user
    - Team = user's team (if any)
    - Starts as visibility="team", approved=False
    """
    user_team = get_user_team(request.user)

    if request.method == "POST":
        form = PolicyForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.team = user_team  # may be None if user not on a team yet
            # start as team-only draft; instructor or team can later publish
            obj.visibility = "team"
            obj.approved = False
            obj.save()
            messages.success(request, "Policy draft created for your team.")
            return redirect("policies:detail", slug=obj.slug)
    else:
        form = PolicyForm()

    return render(request, "policies/edit.html", {"form": form, "policy": None})


@login_required
def policy_edit(request, slug):
    """
    Edit an existing policy.

    Allowed:
      - staff
      - owner
      - any member of the policy's team
    """
    policy = get_object_or_404(Policy, slug=slug)

    if not can_edit_policy(request.user, policy):
        raise Http404("Policy not found")

    if request.method == "POST":
        form = PolicyForm(request.POST, instance=policy)
        if form.is_valid():
            form.save()
            messages.success(request, "Policy updated.")
            return redirect("policies:detail", slug=policy.slug)
    else:
        form = PolicyForm(instance=policy)

    return render(request, "policies/edit.html", {"form": form, "policy": policy})


@login_required
def policy_publish(request, slug):
    """
    Publish a team policy to the whole class.

    - Staff can publish any policy.
    - Team members can publish their own team's policy.

    This sets:
      visibility = "class"
      approved = True
    """
    policy = get_object_or_404(Policy, slug=slug)

    # Only staff OR members of the policy's team may publish
    if not request.user.is_staff:
        user_team = get_user_team(request.user)
        if not (policy.team and user_team == policy.team):
            raise Http404("Policy not found")

    if request.method == "POST":
        policy.visibility = "class"
        policy.approved = True  # once published, treat as approved
        policy.save()
        messages.success(request, "Policy has been published to the class.")
        return redirect("policies:detail", slug=policy.slug)

    # Simple confirmation page
    return render(
        request,
        "policies/publish_confirm.html",
        {"policy": policy},
    )
