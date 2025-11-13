from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from markdownx.utils import markdownify

from .models import DocPage, DocCategory
from .forms import DocPageForm


def docs_index(request):
    """
    List all docs, grouped by category.
    """
    categories = DocCategory.objects.all().order_by("name")
    pages = DocPage.objects.select_related("category").all()
    return render(
        request,
        "docs/index.html",
        {"categories": categories, "pages": pages},
    )


def doc_view(request, slug):
    """
    View a single documentation page.
    """
    page = get_object_or_404(DocPage, slug=slug)
    html = markdownify(page.body)
    return render(
        request,
        "docs/view.html",
        {"page": page, "html": html},
    )


@login_required
def doc_edit(request, slug=None):
    """
    Create or edit a page.

    Rules:
    - Create: any logged-in user.
    - Edit: page author or staff.
    """
    page = None
    if slug:
        page = get_object_or_404(DocPage, slug=slug)
        if not (request.user.is_staff or page.author == request.user):
            messages.error(request, "You are not allowed to edit this page.")
            return redirect("docs:view", slug=page.slug)

    if request.method == "POST":
        form = DocPageForm(request.POST, instance=page)
        if form.is_valid():
            page = form.save(commit=False)
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
