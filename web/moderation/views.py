from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from docs.models import DocPage
from policies.models import Policy

@staff_member_required
def queue(request):
    doc_drafts = DocPage.objects.filter(approved=False).order_by("-updated_at")
    pol_drafts = Policy.objects.filter(approved=False).order_by("-updated_at")
    return render(request, "moderation/queue.html", {"doc_drafts": doc_drafts, "pol_drafts": pol_drafts})

@staff_member_required
def approve_doc(request, pk):
    d = get_object_or_404(DocPage, pk=pk)
    d.approved = True
    d.save()
    return redirect("moderation:queue")

@staff_member_required
def approve_policy(request, pk):
    p = get_object_or_404(Policy, pk=pk)
    p.approved = True
    p.save()
    return redirect("moderation:queue")
