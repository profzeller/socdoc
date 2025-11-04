from django.db import models
from django.contrib.auth.models import User

class Diagram(models.Model):
    title = models.CharField(max_length=120)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    fossflow_url = models.URLField(blank=True)          # e.g., http://localhost:8090/…
    image = models.ImageField(upload_to="diagrams/", blank=True, null=True)  # optional PNG/SVG
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
