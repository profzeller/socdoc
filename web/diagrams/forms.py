# diagrams/forms.py
from django import forms
from django.core.exceptions import ValidationError

from .models import Diagram


class DiagramForm(forms.ModelForm):
    class Meta:
        model = Diagram
        fields = ["title", "image", "external_url", "notes"]
        widgets = {
            "notes": forms.Textarea(
                attrs={
                    "rows": 10,
                    "placeholder": "Describe data flows, trust boundaries, assumptions, etc. (Markdown).",
                }
            ),
            "external_url": forms.URLInput(
                attrs={
                    "placeholder": "Paste your Fossflow / draw.io / Lucidchart link here",
                }
            ),
        }
        labels = {
            "external_url": "External diagram link (Fossflow, draw.io, etc.)",
        }

    def clean(self):
        cleaned = super().clean()
        image = cleaned.get("image")
        url = cleaned.get("external_url", "").strip()

        # Optional: require at least one
        if not image and not url:
            raise ValidationError(
                "Please upload an image or provide an external diagram URL (at least one is required)."
            )

        # Normalize the URL spacing
        cleaned["external_url"] = url
        return cleaned
