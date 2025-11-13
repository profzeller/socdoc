from django import forms
from django.conf import settings
from .models import Team, ClassCode, Profile, ClassConfig


# ------------------------------------------------------
# Class Enrollment Code
# ------------------------------------------------------
class EnrollCodeForm(forms.Form):
    code = forms.CharField(label="Class Code", max_length=64)

    def clean_code(self):
        code = self.cleaned_data["code"].strip()

        # --- Option A: database-stored class codes ---
        if ClassCode.objects.filter(code=code, active=True).exists():
            return code

        # --- Option B: static env var ---
        expected = getattr(settings, "CLASS_ENROLL_CODE", "")
        if expected and code == expected:
            return code

        raise forms.ValidationError("Invalid class code.")


# ------------------------------------------------------
# Create Team
# ------------------------------------------------------
class CreateTeamForm(forms.ModelForm):
    """
    Team creation obeys ClassConfig.
    If students_can_create_teams = False, this form should be blocked by the view.
    """

    class Meta:
        model = Team
        fields = ["name"]

    def clean(self):
        config = ClassConfig.get_solo()
        if not config.students_can_create_teams:
            raise forms.ValidationError("Students are not allowed to create teams right now.")
        return super().clean()


# ------------------------------------------------------
# Join Team via join_code
# ------------------------------------------------------
class JoinTeamForm(forms.Form):
    join_code = forms.CharField(
        max_length=32,
        label="Team Join Code",
        help_text="Enter the join code provided by your team leader."
    )

    def clean_join_code(self):
        code = self.cleaned_data["join_code"].strip()

        try:
            team = Team.objects.get(join_code=code)
        except Team.DoesNotExist:
            raise forms.ValidationError("Invalid join code.")

        self.team = team  # store for the view
        return code


# ------------------------------------------------------
# Profile edit form (optional)
# ------------------------------------------------------
class ProfileForm(forms.ModelForm):
    """
    Lets users edit display_name + role_in_soc.
    """
    class Meta:
        model = Profile
        fields = ["display_name", "role_in_soc"]
        widgets = {
            "display_name": forms.TextInput(attrs={"placeholder": "Your preferred name"}),
            "role_in_soc": forms.TextInput(attrs={"placeholder": "Example: IR Lead, SIEM Analyst, etc."}),
        }
