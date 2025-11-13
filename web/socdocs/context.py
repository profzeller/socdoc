# socdocs/context.py
from . import settings as project_settings  # if you need; or just import directly
from accounts.models import Profile, ClassConfig


def team_badge(request):
    team = None
    if request.user.is_authenticated:
        prof, _ = Profile.objects.get_or_create(user=request.user)
        team = prof.team

    config = ClassConfig.get_solo()

    return {
        "CURRENT_TEAM": team,
        "CLASS_CONFIG": config,
    }
