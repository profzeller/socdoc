from django.db import models
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from django.utils.text import slugify

from accounts.models import Team   # <-- use the Team model from accounts


class Policy(models.Model):
    CATEGORY_CHOICES = [
        ("IR", "Incident Response"),
        ("AC", "Access Control"),
        ("LM", "Log Management"),
        ("CC", "Change Control"),
        ("NW", "Network Security"),
        ("BK", "Backup & Recovery"),
        ("OT", "Other"),
    ]

    VISIBILITY_CHOICES = [
        ("team", "Team-only"),
        ("class", "Class-wide"),
        ("global", "Public"),
    ]

    category = models.CharField(
        max_length=2,
        choices=CATEGORY_CHOICES,
        default="OT",
    )
    title = models.CharField(max_length=200)

    # Make slug auto-fill from title if not provided
    slug = models.SlugField(unique=True, blank=True)

    # original owner field (keep)
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="policies_owned",
    )

    # NEW: link a policy to a team
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="policies",
    )

    content = MarkdownxField()

    # NEW: team/class/global visibility
    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default="team",
    )

    approved = models.BooleanField(default=False)
    version = models.CharField(max_length=20, default="1.0")
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def html(self):
        return markdownify(self.content)

    class Meta:
        ordering = ["category", "title"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_category_display()} — {self.title}"
