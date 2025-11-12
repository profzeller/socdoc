# accounts/middleware.py
from django.shortcuts import redirect

class ClassCodeGateMiddleware:
    """
    Require a class code only on SIGNUP flows.
    Allow all LOGIN flows without a code.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        q = request.GET

        # Never gate admin, static, media
        if path.startswith("/admin/") or path.startswith("/static/") or path.startswith("/media/"):
            return self.get_response(request)

        # Authenticated users pass through
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            return self.get_response(request)

        # ----- SIGNUP routes we want to protect with class code -----
        is_email_signup = path.startswith("/accounts/signup/")
        is_social_signup_finish = path.startswith("/accounts/social/signup/")
        is_discord_signup = path.startswith("/accounts/discord/login/") and q.get("process") == "signup"

        requires_code = is_email_signup or is_social_signup_finish or is_discord_signup

        # ----- LOGIN and other flows we should NOT gate -----
        # e.g., /accounts/login/, /accounts/discord/login/?process=login,
        # password reset, etc., simply pass through.

        if requires_code and not request.session.get("class_ok"):
            # remember where they were headed, then send to enroll page
            request.session["after_enroll_next"] = request.get_full_path() or "/"
            return redirect("accounts:enroll")

        return self.get_response(request)
