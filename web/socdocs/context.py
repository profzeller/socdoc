def team_badge(request):
    if not request.user.is_authenticated:
        return {}
    t = request.user.teams.first()
    return {"CURRENT_TEAM": t}
