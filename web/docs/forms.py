from django import forms
from .models import DocPage, DocCategory
from django.utils.text import slugify


class DocPageForm(forms.ModelForm):
    # Override: plain ChoiceField, not ModelChoiceField
    category = forms.ChoiceField(
        choices=[],
        required=True,
        label="Category",
    )

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
            (str(c.id), c.name) for c in categories
        ] + [("NEW", "➕ Create new category…")]

        self.fields["category"].choices = choices

    def clean(self):
        cleaned = super().clean()
        raw_category = cleaned.get("category")
        new_category = (cleaned.get("new_category") or "").strip()

        # Nothing selected at all
        if not raw_category:
            raise forms.ValidationError("Please choose a category.")

        # User selected "Create new category…"
        if raw_category == "NEW":
            if not new_category:
                raise forms.ValidationError(
                    "Please enter a name for the new category."
                )
            cat_obj, _ = DocCategory.objects.get_or_create(
                name=new_category,
                defaults={"slug": slugify(new_category)},
            )
            cleaned["category"] = cat_obj
            return cleaned

        # Existing category chosen → look up by ID
        try:
            cat_obj = DocCategory.objects.get(id=raw_category)
        except DocCategory.DoesNotExist:
            raise forms.ValidationError("Invalid category selected.")

        cleaned["category"] = cat_obj
        return cleaned