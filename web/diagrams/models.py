from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify

from accounts.models import Team  # use the team model from accounts


class Diagram(models.Model):
    VISIBILITY_CHOICES = [
        ("team", "Team only"),
        ("class", "Class (published)"),
        ("global", "Global/public"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)

    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="diagrams",
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="diagrams",
    )

    # Either upload an image OR paste a URL to Lucidchart / draw.io / etc.
    image = models.ImageField(
        upload_to="diagrams/",
        blank=True,
        null=True,
        help_text="Upload a PNG/JPG export of your diagram.",
    )
    external_url = models.URLField(
        blank=True,
        help_text="Optional link to Lucidchart, draw.io, Excalidraw, etc.",
    )

    notes = MarkdownxField(
        blank=True,
        help_text="Describe the diagram, assumptions, data flows, etc. (Markdown).",
    )

    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default="team",
    )
    approved = models.BooleanField(
        default=False,
        help_text="Once approved+published, visible to the whole class.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def html_notes(self):
        return markdownify(self.notes or "")

    def __str__(self):
        return self.title
