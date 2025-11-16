from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from markdownx.utils import markdownify

from accounts.models import Profile
from .forms import DocPageForm
from .models import DocCategory, DocPage


def _user_team(user):
    """Return the user's team or None (handles missing profile)."""
    if not user.is_authenticated:
        return None
    try:
        return user.profile.team
    except Profile.DoesNotExist:
        return None


def docs_index(request):
    qs = DocPage.objects.select_related("category", "team").order_by("title")

    # Docs visible to the whole class (includes global docs with no team)
    public_pages = qs.filter(visibility="class")

    # Docs for the current user's team (team-only + published)
    team_pages = None
    profile = getattr(request.user, "profile", None)
    if profile and profile.team_id:
        team_pages = qs.filter(team=profile.team)

    categories = DocCategory.objects.order_by("name")

    context = {
        "categories": categories,
        "public_pages": public_pages,
        "team_pages": team_pages,
    }
    return render(request, "docs/index.html", context)


def doc_view(request, slug):
    """
    - Published (visibility=class): visible to everyone.
    - Team-only (visibility=team):
         - Staff OR members of that team only.
    - Global instructor docs: typically visibility=class, team=None.
    """
    page = get_object_or_404(DocPage, slug=slug)

    if page.visibility == DocPage.VISIBILITY_TEAM and page.team:
        if not request.user.is_staff:
            team = _user_team(request.user)
            if team != page.team:
                raise Http404("Document not found")

    html = markdownify(page.body)
    return render(request, "docs/view.html", {"page": page, "html": html})


@login_required
def doc_create(request):
    """
    - Non-staff must belong to a team to create docs.
    - Student docs default: team-only (visibility=team, team=<their team>).
    - Staff can create global docs (team=None) which we usually treat
      as published to class.
    """
    team = _user_team(request.user)

    if not request.user.is_staff and not team:
        messages.error(
            request,
            "You must join or create a team before creating documentation.",
        )
        return redirect("accounts:profile")

    if request.method == "POST":
        form = DocPageForm(request.POST)
        if form.is_valid():
            page = form.save(commit=False)
            page.author = request.user

            if request.user.is_staff:
                # Instructor docs: default to published, unless you prefer team-only.
                if page.team is None:
                    page.visibility = DocPage.VISIBILITY_CLASS
            else:
                # Student docs: locked to their team, team-only initially.
                page.team = team
                page.visibility = DocPage.VISIBILITY_TEAM

            page.save()
            messages.success(request, "Page created.")
            return redirect("docs:detail", slug=page.slug)
    else:
        form = DocPageForm()

    return render(request, "docs/edit.html", {"form": form, "is_create": True})


@login_required
def doc_edit(request, slug):
    page = get_object_or_404(DocPage, slug=slug)

    # -------- Permission check --------
    if not request.user.is_staff:
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            return HttpResponseForbidden("You do not have permission to edit this page.")

        # Must belong to the same team as the page
        if not page.team or profile.team_id != page.team_id:
            return HttpResponseForbidden("You do not have permission to edit this page.")

    # -------- Handle form --------
    if request.method == "POST":
        form = DocPageForm(request.POST, instance=page)
        if form.is_valid():
            page = form.save(commit=False)

            # Ensure a category is resolved if "NEW" was chosen
            cat_choice = form.cleaned_data.get("category")
            new_cat_name = form.cleaned_data.get("new_category", "").strip()

            # DocPageForm.clean() should already normalize this, but this is safe:
            if isinstance(cat_choice, DocCategory):
                page.category = cat_choice
            elif cat_choice == "NEW" and new_cat_name:
                cat, _ = DocCategory.objects.get_or_create(name=new_cat_name)
                page.category = cat

            # Keep existing team/visibility as-is; just update content.
            if not page.author:
                page.author = request.user

            page.save()
            messages.success(request, "Page updated.")
            return redirect("docs:detail", slug=page.slug)
    else:
        form = DocPageForm(instance=page)

    return render(request, "docs/edit.html", {"form": form, "page": page})



@login_required
def doc_publish(request, slug):
    """
    Publish a team doc to the whole class.
    After this:
      - Everyone can view it.
      - Only staff can edit it.
    """
    page = get_object_or_404(DocPage, slug=slug)
    team = _user_team(request.user)

    # Only staff OR members of the owning team can publish
    if not request.user.is_staff:
        if not (page.team and team == page.team):
            raise Http404("Document not found")

    if request.method == "POST":
        page.visibility = DocPage.VISIBILITY_CLASS
        page.save()
        messages.success(request, "Page published to the whole class.")
        return redirect("docs:detail", slug=page.slug)

    return render(request, "docs/confirm_publish.html", {"page": page})
