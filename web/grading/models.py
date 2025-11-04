from django.db import models
from django.contrib.auth.models import User

class Milestone(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateField(null=True, blank=True)
    max_points = models.PositiveIntegerField(default=100)

    def __str__(self):
        return self.title

class Submission(models.Model):
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    notes = models.TextField(blank=True)
    docs_url = models.URLField(blank=True)
    diagram = models.URLField(blank=True)
    policies = models.URLField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    graded = models.BooleanField(default=False)
    score = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.student.username} - {self.milestone.title}"
