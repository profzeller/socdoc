# diagrams/forms.py
from django import forms
from django.core.exceptions import ValidationError

from .models import Diagram


class DiagramForm(forms.ModelForm):
    """
    Form for creating/updating a Diagram.

    Rules:
    - title: required
    - At least one of (image, external_url) should be provided.
    - notes is Markdown.
    """

    class Meta:
        model = Diagram
        fields = ["title", "image", "external_url", "notes"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "e.g. SOC Network Diagram"}),
            "external_url": forms.URLInput(
                attrs={"placeholder": "Link to Lucidchart / draw.io / Excalidraw (optional)"}
            ),
            "notes": forms.Textarea(
                attrs={"rows": 12, "placeholder": "Describe the diagram, flows, assumptions, etc. (Markdown)"}
            ),
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
