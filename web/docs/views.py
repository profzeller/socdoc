from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import ModelForm
from .models import DocPage
from django.http import Http404

class DocForm(ModelForm):
    class Meta:
        model = DocPage
        fields = ["title","slug","content","milestone"]

def page_list(request):
    pages = DocPage.objects.filter(approved=True).order_by("title")
    drafts = []
    if request.user.is_authenticated:
        drafts = DocPage.objects.filter(author=request.user, approved=False).order_by("-updated_at")
    return render(request, "docs/list.html", {"pages": pages, "drafts": drafts})

def page_detail(request, slug):
    page = get_object_or_404(DocPage, slug=slug)
    if not page.approved and (not request.user.is_authenticated or (request.user != page.author and not request.user.is_staff)):
        raise Http404()
    return render(request, "docs/detail.html", {"page": page})

@login_required
def page_create(request):
    if request.method == "POST":
        form = DocForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.author = request.user
            obj.approved = False
            obj.save()
            return redirect("docs:list")
    else:
        form = DocForm()
    return render(request, "docs/edit.html", {"form": form})
