# diagrams/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib import messages

from .models import Diagram
from .forms import DiagramForm


# -------------------------
# Helpers
# -------------------------

def get_user_team(user):
    """Return the accounts.Team for this user, or None."""
    prof = getattr(user, "profile", None)
    return getattr(prof, "team", None) if prof else None


def can_view_diagram(user, diagram: Diagram) -> bool:
    """
    Centralized permission check for viewing a diagram.

    - Approved + class/global => anyone can view
    - team-only or unapproved => only staff, owner, or team members
    """
    # Staff can always see
    if user.is_authenticated and user.is_staff:
        return True

    # If not approved yet (draft)
    if not diagram.approved:
        if not user.is_authenticated:
            return False
        if user == diagram.owner:
            return True
        user_team = get_user_team(user)
        if diagram.team and user_team == diagram.team:
            return True
        return False

    # Approved: handle by visibility
    if diagram.visibility in ("class", "global"):
        # visible to everyone once published to class/global
        return True

    # team-only visibility
    if diagram.visibility == "team":
        if not user.is_authenticated:
            return False
        if user == diagram.owner:
            return True
        user_team = get_user_team(user)
        if diagram.team and user_team == diagram.team:
            return True
        return False

    # Fallback
    return False


def can_edit_diagram(user, diagram: Diagram) -> bool:
    """
    Who can edit a diagram?
    - staff
    - owner
    - any member of the diagram's team
    (Even after it's published to class, team + staff can still edit.)
    """
    if not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    if user == diagram.owner:
        return True
    user_team = get_user_team(user)
    if diagram.team and user_team == diagram.team:
        return True
    return False


# -------------------------
# Views
# -------------------------

def diagram_list(request):
    """
    Show:
      - All approved diagrams with visibility class/global for everyone.
      - If user is on a team, also show their team's diagrams (drafts/team-only).
    """
    # published diagrams (visible to class/global)
    published = Diagram.objects.filter(
        approved=True,
        visibility__in=["class", "global"],
    ).order_by("title")

    user_team = get_user_team(request.user) if request.user.is_authenticated else None

    team_diagrams = []
    if user_team:
        team_diagrams = (
            Diagram.objects.filter(team=user_team)
            .order_by("-updated_at")
        )

    return render(
        request,
        "diagrams/list.html",
        {
            "published": published,
            "team_diagrams": team_diagrams,
            "user_team": user_team,
        },
    )


def diagram_detail(request, pk):
    diagram = get_object_or_404(Diagram, pk=pk)

    if not can_view_diagram(request.user, diagram):
        raise Http404("Diagram not found")

    return render(request, "diagrams/detail.html", {"diagram": diagram})


@login_required
def diagram_create(request):
    """
    Create a new diagram for the current user's team.
    Diagrams start as team-only drafts; instructor can later approve/publish.
    """
    user_team = get_user_team(request.user)

    if request.method == "POST":
        form = DiagramForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.team = user_team   # may be None if user isn't on a team
            obj.visibility = "team"
            obj.approved = False
            obj.save()
            messages.success(request, "Diagram created for your team.")
            return redirect("diagrams:detail", pk=obj.pk)
    else:
        form = DiagramForm()

    return render(request, "diagrams/edit.html", {"form": form, "diagram": None})


@login_required
def diagram_edit(request, pk):
    """
    Edit an existing diagram.
    Staff, owner, or team members may edit (even after publish).
    """
    diagram = get_object_or_404(Diagram, pk=pk)

    if not can_edit_diagram(request.user, diagram):
        raise Http404("Diagram not found")

    if request.method == "POST":
        form = DiagramForm(request.POST, request.FILES, instance=diagram)
        if form.is_valid():
            form.save()
            messages.success(request, "Diagram updated.")
            return redirect("diagrams:detail", pk=diagram.pk)
    else:
        form = DiagramForm(instance=diagram)

    return render(request, "diagrams/edit.html", {"form": form, "diagram": diagram})


@login_required
def diagram_publish(request, pk):
    """
    Publish a team diagram to the whole class.
    - Staff can publish any diagram.
    - Team members (owner or same team) can publish their team’s diagram.

    This sets visibility="class" and approved=True.
    """
    diagram = get_object_or_404(Diagram, pk=pk)

    # Only staff OR members of the diagram's team may publish
    if not request.user.is_staff:
        user_team = get_user_team(request.user)
        if not (diagram.team and user_team == diagram.team):
            raise Http404("Diagram not found")

    if request.method == "POST":
        diagram.visibility = "class"
        diagram.approved = True
        diagram.save()
        messages.success(request, "Diagram has been published to the class.")
        return redirect("diagrams:detail", pk=diagram.pk)

    # Simple confirmation page
    return render(
        request,
        "diagrams/publish_confirm.html",
        {"diagram": diagram},
    )
