from django.contrib.auth.models import User
from django.db import models
import secrets

def gen_code(n=8):
    return secrets.token_urlsafe(n).rstrip("_-")

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    join_code = models.CharField(max_length=32, unique=True, default=gen_code)
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="owned_teams")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return f"{self.name}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name="members")
    discord_id = models.CharField(max_length=50, blank=True, default="")

    def __str__(self): return self.user.username

# OPTIONAL: if you want multiple/rotating class codes
class ClassCode(models.Model):
    code = models.CharField(max_length=64, unique=True)
    label = models.CharField(max_length=120, blank=True)
    active = models.BooleanField(default=True)
    def __str__(self): return f"{self.code} ({'active' if self.active else 'inactive'})"
