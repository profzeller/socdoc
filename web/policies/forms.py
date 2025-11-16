from django import forms
from .models import PolicyPage, PolicyCategory


class PolicyPageForm(forms.ModelForm):
    NEW_CATEGORY_VALUE = "NEW"

    new_category = forms.CharField(
        max_length=100,
        required=False,
        label="New Category",
    )

    class Meta:
        model = PolicyPage
        fields = ["title", "category", "new_category", "body"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        cats = PolicyCategory.objects.all().order_by("name")
        choices = [("", "Select a category")] + [
            (c.id, c.name) for c in cats
        ] + [(self.NEW_CATEGORY_VALUE, "➕ Create new category…")]

        self.fields["category"].choices = choices
        self.fields["category"].required = False
        self.fields["new_category"].widget.attrs["style"] = "display:none;"

    def clean(self):
        cleaned = super().clean()
        category = cleaned.get("category")
        new_category = cleaned.get("new_category", "").strip()

        if category == self.NEW_CATEGORY_VALUE:
            if not new_category:
                raise forms.ValidationError(
                    "Please enter a name for the new category."
                )
        elif not category:
            raise forms.ValidationError("Please choose a category.")

        return cleaned

    def save(self, commit=True, author=None, team=None):
        """
        Handles NEW-category creation and attaches author/team.
        """
        instance = super().save(commit=False)
        category = self.cleaned_data.get("category")
        new_category = self.cleaned_data.get("new_category", "").strip()

        if category == self.NEW_CATEGORY_VALUE:
            cat_obj, _ = PolicyCategory.objects.get_or_create(name=new_category)
            instance.category = cat_obj
        else:
            if category:
                instance.category = PolicyCategory.objects.get(id=category)

        if author is not None:
            instance.author = author
        if team is not None:
            instance.team = team

        if commit:
            instance.save()
        return instance
