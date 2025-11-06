from django import forms
from django.conf import settings
from .models import Team, ClassCode

class EnrollCodeForm(forms.Form):
    code = forms.CharField(label="Class Code", max_length=64)

    def clean_code(self):
        code = self.cleaned_data["code"].strip()
        # Accept from DB if using ClassCode table
        if ClassCode.objects.filter(code=code, active=True).exists():
            return code
        # Or fallback to single env var
        expected = getattr(settings, "CLASS_ENROLL_CODE", "")
        if expected and code == expected:
            return code
        raise forms.ValidationError("Invalid class code.")

class CreateTeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["name"]

class JoinTeamForm(forms.Form):
    join_code = forms.CharField(max_length=32, label="Team Join Code")
