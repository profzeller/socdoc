# diagrams/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib import messages
from django.conf import settings

from .models import Diagram
from .forms import DiagramForm
from accounts.models import Team


# -------- Helper to get the accounts.Team --------
def get_user_team(user):
    """
    Return the accounts.Team for this user, or None.
    Uses the Profile.team relationship we use everywhere else
    (like the navbar).
    """
    prof = getattr(user, "profile", None)
    return getattr(prof, "team", None) if prof else None


def can_edit_diagram(user, diagram: Diagram) -> bool:
    """
    Who can edit a diagram?
    - staff
    - owner
    - any member of the diagram's team
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


def can_view_diagram(user, diagram: Diagram) -> bool:
    """
    View rules:
    - Approved + class/global: anyone can view (even anon).
    - Team-only or unapproved: only owner, team members, or staff.
    """
    # Staff can always see
    if user.is_authenticated and user.is_staff:
        return True

    # Unapproved
    if not diagram.approved:
        if not user.is_authenticated:
            return False
        if can_edit_diagram(user, diagram):
            return True
        return False

    # Approved: handle by visibility
    if diagram.visibility in ("class", "global"):
        return True

    if diagram.visibility == "team":
        if not user.is_authenticated:
            return False
        if can_edit_diagram(user, diagram):
            return True
        return False

    return False


def diagram_list(request):
    """
    Show:
      - All approved class/global diagrams to everyone.
      - Team-only / draft diagrams for the current user's team (if any).
    """

    # Approved diagrams visible to the whole class/global
    published = Diagram.objects.filter(
        approved=True,
        visibility__in=["class", "global"],
    ).order_by("title")

    user_team = None
    team_diagrams = []

    if request.user.is_authenticated:
        user_team = get_user_team(request.user)
        if user_team:
            # Team’s own diagrams (including non-approved or team-only)
            team_diagrams = (
                Diagram.objects.filter(team=user_team)
                .order_by("title")
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


def diagram_detail(request, slug):
    diagram = get_object_or_404(Diagram, slug=slug)

    if not can_view_diagram(request.user, diagram):
        raise Http404("Diagram not found")

    return render(request, "diagrams/detail.html", {"diagram": diagram})


@login_required
def diagram_create(request):
    user_team = get_user_team(request.user)

    if request.method == "POST":
        form = DiagramForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.team = user_team  # may be None
            obj.visibility = "team"
            obj.approved = False
            obj.save()
            messages.success(request, "Diagram created for your team.")
            return redirect("diagrams:detail", slug=obj.slug)
    else:
        form = DiagramForm()

    return render(
        request,
        "diagrams/edit.html",
        {
            "form": form,
            "diagram": None,
            "fossflow_url": getattr(settings, "FOSSFLOW_URL", ""),
        },
    )


@login_required
def diagram_edit(request, slug):
    diagram = get_object_or_404(Diagram, slug=slug)

    if not can_edit_diagram(request.user, diagram):
        raise Http404("Diagram not found")

    if request.method == "POST":
        form = DiagramForm(request.POST, request.FILES, instance=diagram)
        if form.is_valid():
            form.save()
            messages.success(request, "Diagram updated.")
            return redirect("diagrams:detail", slug=diagram.slug)
    else:
        form = DiagramForm(instance=diagram)

    return render(
        request,
        "diagrams/edit.html",
        {
            "form": form,
            "diagram": diagram,
            "fossflow_url": getattr(settings, "FOSSFLOW_URL", ""),
        },
    )


@login_required
def diagram_publish(request, slug):
    """
    Publish a team diagram to the whole class.
    - Staff can publish any diagram.
    - Team members can publish their own team’s diagram.
    """
    diagram = get_object_or_404(Diagram, slug=slug)

    if not request.user.is_staff:
        user_team = get_user_team(request.user)
        if not (diagram.team and user_team == diagram.team):
            raise Http404("Diagram not found")

    if request.method == "POST":
        diagram.visibility = "class"
        diagram.approved = True
        diagram.save()
        messages.success(request, "Diagram has been published to the class.")
        return redirect("diagrams:detail", slug=diagram.slug)

    return render(
        request,
        "diagrams/publish_confirm.html",
        {"diagram": diagram},
    )
