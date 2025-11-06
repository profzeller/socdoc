from django.shortcuts import redirect

GATED_PATH_PREFIXES = (
    "/accounts/discord/",  # social login
    "/accounts/login/",
    "/accounts/signup/",
)

class ClassCodeGateMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # never gate admin or static/media
        if path.startswith("/admin/") or path.startswith("/static/") or path.startswith("/media/"):
            return self.get_response(request)

        # if user is authenticated, nothing to do
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            return self.get_response(request)

        # gate only selected account flows
        if any(path.startswith(p) for p in GATED_PATH_PREFIXES):
            if not request.session.get("class_ok"):
                request.session["after_enroll_next"] = path or "/"
                return redirect("accounts:enroll")

        return self.get_response(request)
