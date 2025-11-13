# accounts/models.py
from django.contrib.auth.models import User
from django.db import models
import secrets


def gen_code(n=8):
    return secrets.token_urlsafe(n).rstrip("_-")


class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    join_code = models.CharField(max_length=32, unique=True, default=gen_code)
    owner = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="owned_teams",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    team = models.ForeignKey(
        Team,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="members",
    )
    discord_id = models.CharField(max_length=50, blank=True, default="")

    # Optional niceties for the profile page:
    display_name = models.CharField(max_length=150, blank=True)
    role_in_soc = models.CharField(
        max_length=150,
        blank=True,
        help_text="Student's role in the SOC (e.g., 'SIEM engineer', 'IR lead').",
    )

    def __str__(self):
        return self.display_name or self.user.username


# OPTIONAL: if you want multiple/rotating class codes
class ClassCode(models.Model):
    code = models.CharField(max_length=64, unique=True)
    label = models.CharField(max_length=120, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} ({'active' if self.active else 'inactive'})"


class ClassConfig(models.Model):
    """
    Global configuration for this class / course.
    Controls whether students can self-manage teams.
    """

    students_can_create_teams = models.BooleanField(
        default=True,
        help_text="If disabled, only staff can create/assign teams.",
    )
    # you can add more toggles later if you want

    class Meta:
        verbose_name = "Class configuration"
        verbose_name_plural = "Class configuration"

    def __str__(self):
        return "Class configuration"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
