from django.db import models
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from django.utils.text import slugify
from accounts.models import Team


class DocCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class DocPage(models.Model):
    VISIBILITY_TEAM = "team"
    VISIBILITY_CLASS = "class"  # published to whole class

    VISIBILITY_CHOICES = [
        (VISIBILITY_TEAM, "Team only"),
        (VISIBILITY_CLASS, "Published to class"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(
        DocCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    # Which team owns this doc. Null = instructor/global doc.
    team = models.ForeignKey(
        Team,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="docs",
        help_text="Leave blank for instructor/global docs.",
    )

    # NEW: who can see it
    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default=VISIBILITY_TEAM,
    )

    body = MarkdownxField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
