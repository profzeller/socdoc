from allauth.account.forms import SignupForm
from django import forms
from django.conf import settings

class ClassCodeSignupForm(SignupForm):
    class_code = forms.CharField(
        label="Class Code",
        max_length=64,
        help_text="Ask your instructor for the current class code.",
    )

    def clean_class_code(self):
        code = self.cleaned_data.get("class_code", "").strip()
        expected = getattr(settings, "CLASS_ENROLL_CODE", "").strip()
        if not expected:
            # If you forgot to set it, fail closed so the internet can't register
            raise forms.ValidationError("Class enrollment is currently closed.")
        if code != expected:
            raise forms.ValidationError("Invalid class code.")
        return code

    # If you want to auto-add users to a default group/team, you can override save() later.
