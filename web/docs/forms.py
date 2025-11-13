from django import forms
from .models import DocPage


class DocPageForm(forms.ModelForm):
    class Meta:
        model = DocPage
        fields = ["title", "category", "body"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "e.g. Wazuh Deployment Overview"}),
        }
