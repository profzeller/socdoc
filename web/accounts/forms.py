from django import forms
from django.conf import settings

from .models import Team, ClassCode, Profile, ClassConfig

# Allauth imports for custom signup forms
from allauth.account.forms import SignupForm as AllauthSignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupBase


# ------------------------------------------------------
# Shared validator for class codes
# ------------------------------------------------------
def validate_class_code(raw_code: str) -> str:
    """
    Central place to validate a class code.

    Accepts either:
    - A record in ClassCode with active=True
    - Or the single env var CLASS_ENROLL_CODE
    """
    code = (raw_code or "").strip()

    # Option A: DB-backed codes
    if ClassCode.objects.filter(code=code, active=True).exists():
        return code

    # Option B: single env var
    expected = getattr(settings, "CLASS_ENROLL_CODE", "")
    if expected and code == expected:
        return code

    raise forms.ValidationError("Invalid class code.")


# ------------------------------------------------------
# Enroll gate form (if you still use /accounts/enroll/)
# ------------------------------------------------------
class EnrollCodeForm(forms.Form):
    code = forms.CharField(label="Class Code", max_length=64)

    def clean_code(self):
        return validate_class_code(self.cleaned_data["code"])


# ------------------------------------------------------
# ACCOUNT SIGNUP (email/password path) with class code
# ------------------------------------------------------
class ClassCodeSignupForm(AllauthSignupForm):
    """
    Used for the regular account signup flow (email/password).
    Adds a class_code field and validates it.
    """

    class_code = forms.CharField(
        label="Class Code",
        max_length=64,
        help_text="Enter the class code your instructor gave you.",
    )

    def clean_class_code(self):
        return validate_class_code(self.cleaned_data["class_code"])

    def save(self, request):
        # We don't store the class_code on the user, it's just a gate.
        self.cleaned_data.pop("class_code", None)
        user = super().save(request)
        return user


# ------------------------------------------------------
# SOCIAL SIGNUP (Discord) with class code
# ------------------------------------------------------
class SocialClassCodeSignupForm(SocialSignupBase):
    """
    Used for the Discord 3rd-party signup screen.

    - Shows ONLY the class_code field to the user.
    - Hides email (Discord email is still captured but not editable).
    """

    class_code = forms.CharField(
        label="Class Code",
        max_length=64,
        help_text="Enter the class code your instructor gave you.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Hide email field from the UI (Discord already provided it)
        if "email" in self.fields:
            self.fields["email"].widget = forms.HiddenInput()

        # If username is prefilled from Discord and you don't want students
        # to edit it here, you could also hide it:
        # if "username" in self.fields:
        #     self.fields["username"].widget = forms.HiddenInput()

    def clean_class_code(self):
        return validate_class_code(self.cleaned_data["class_code"])

    def save(self, request):
        # Discard class_code after validation
        self.cleaned_data.pop("class_code", None)
        user = super().save(request)
        return user


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
        help_text="Enter the join code provided by your team leader.",
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
            "display_name": forms.TextInput(
                attrs={"placeholder": "Your preferred name"}
            ),
            "role_in_soc": forms.TextInput(
                attrs={"placeholder": "Example: IR Lead, SIEM Analyst, etc."}
            ),
        }
