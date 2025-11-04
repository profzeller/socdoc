from django.db import models
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify

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

    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default="OT")
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    content = MarkdownxField()
    approved = models.BooleanField(default=False)
    version = models.CharField(max_length=20, default="1.0")  # simple version string
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def html(self):
        return markdownify(self.content)

    class Meta:
        ordering = ["category", "title"]

    def __str__(self):
        return f"{self.get_category_display()} — {self.title}"
