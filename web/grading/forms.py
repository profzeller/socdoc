from django import forms
from .models import Milestone


class DocSubmissionForm(forms.Form):
    """
    Simple form: choose which milestone this doc should count for.
    One submission per (milestone, student) is still enforced by the model.
    """
    milestone = forms.ModelChoiceField(
        queryset=Milestone.objects.all(),
        empty_label="Select a milestone",
        label="Milestone",
        help_text="Choose which milestone this documentation is for."
    )
