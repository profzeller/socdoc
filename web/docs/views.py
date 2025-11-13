from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from markdownx.utils import markdownify

from .models import DocPage, DocCategory
from .forms import DocPageForm
from accounts.models import Profile   # 👈 NEW


def docs_index(request):
    categories = DocCategory.objects.all().order_by("name")
    pages = DocPage.objects.select_related("category", "team", "author").all()
    return render(
        request,
        "docs/index.html",
        {"categories": categories, "pages": pages},
    )


def doc_view(request, slug):
    page = get_object_or_404(DocPage, slug=slug)
    html = markdownify(page.body)
    return render(
        request,
        "docs/view.html",
        {"page": page, "html": html},
    )


def _user_team(user):
    """Helper: safe way to get a user's Team (or None)."""
    if not user.is_authenticated:
        return None
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile.team


@login_required
def doc_edit(request, slug=None):
    """
    Create or edit a page.

    Rules:
    - Create: any logged-in user.
    - Edit: staff OR any member of the owning team
            (fallback: original author if no team set).
    """
    page = None
    if slug:
        page = get_object_or_404(DocPage, slug=slug)
        user_team = _user_team(request.user)

        # Permission check
        allowed = False
        if request.user.is_staff:
            allowed = True
        elif page.team and user_team and page.team_id == user_team.id:
            allowed = True
        elif not page.team and page.author == request.user:
            # old pages or special cases
            allowed = True

        if not allowed:
            messages.error(request, "You are not allowed to edit this page.")
            return redirect("docs:view", slug=page.slug)

    if request.method == "POST":
        form = DocPageForm(request.POST, instance=page)
        if form.is_valid():
            page = form.save(commit=False)

            # Attach team on create, or keep existing
            if page.pk is None:
                # New page: attach creator's team (if any)
                creator_team = _user_team(request.user)
                if creator_team:
                    page.team = creator_team

            if page.author_id is None:
                page.author = request.user

            page.save()
            messages.success(request, "Page saved.")
            return redirect("docs:view", slug=page.slug)
    else:
        form = DocPageForm(instance=page)

    return render(
        request,
        "docs/edit.html",
        {"form": form, "page": page},
    )
