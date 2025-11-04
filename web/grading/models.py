from django.db import models
from django.contrib.auth.models import User

class Team(models.Model):
    name = models.CharField(max_length=64, unique=True)
    members = models.ManyToManyField(User, related_name="teams", blank=True)
    def __str__(self):
        return self.name

class Milestone(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateField(null=True, blank=True)
    max_points = models.PositiveIntegerField(default=100)
    def __str__(self):
        return self.title

class Criterion(models.Model):
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE, related_name="criteria")
    label = models.CharField(max_length=200)
    max_points = models.PositiveIntegerField(default=10)
    weight = models.FloatField(default=1.0)
    def __str__(self):
        return f"{self.milestone.title} · {self.label}"

class Submission(models.Model):
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name="submissions")
    notes = models.TextField(blank=True)
    docs_url = models.URLField(blank=True)
    diagram = models.URLField(blank=True)
    policies = models.URLField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    graded = models.BooleanField(default=False)
    score = models.FloatField(default=0)

    class Meta:
        unique_together = [("milestone", "student")]

    def __str__(self):
        return f"{self.student.username} – {self.milestone.title}"

class Evidence(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="evidence")
    title = models.CharField(max_length=200)
    link = models.URLField(blank=True)
    file = models.FileField(upload_to="evidence/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class CriterionScore(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="criterion_scores")
    criterion = models.ForeignKey(Criterion, on_delete=models.CASCADE)
    points = models.FloatField(default=0)
    comment = models.TextField(blank=True)

    class Meta:
        unique_together = [("submission", "criterion")]
