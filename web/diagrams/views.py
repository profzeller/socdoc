from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import ModelForm
from .models import Diagram

class DiagramForm(ModelForm):
    class Meta:
        model = Diagram
        fields = ["title","fossflow_url","image","notes"]

def diagram_list(request):
    items = Diagram.objects.all()
    return render(request, "diagrams/list.html", {"items": items})

def diagram_detail(request, pk):
    d = get_object_or_404(Diagram, pk=pk)
    return render(request, "diagrams/detail.html", {"d": d})

@login_required
def diagram_create(request):
    if request.method == "POST":
        form = DiagramForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            return redirect("diagrams:list")
    else:
        form = DiagramForm()
    return render(request, "diagrams/edit.html", {"form": form})
