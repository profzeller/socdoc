from django import forms
from .models import DocPage, DocCategory


class DocPageForm(forms.ModelForm):
    new_category = forms.CharField(
        max_length=100,
        required=False,
        label="New Category",
    )

    class Meta:
        model = DocPage
        fields = ["title", "category", "new_category", "body"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Build choices dynamically with a "New Category" option
        categories = DocCategory.objects.all().order_by("name")
        choices = [("", "Select a category")] + [
            (c.id, c.name) for c in categories
        ] + [("NEW", "➕ Create new category…")]

        self.fields["category"].choices = choices

    def clean(self):
        cleaned = super().clean()
        category = cleaned.get("category")
        new_category = cleaned.get("new_category", "").strip()

        if category == "NEW":
            if not new_category:
                raise forms.ValidationError("Please enter a name for the new category.")
        elif not category:
            raise forms.ValidationError("Please choose a category.")

        return cleaned
