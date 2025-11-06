from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class MySocialAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form=form)
        try:
            uid = sociallogin.account.uid
            prof = user.profile
            if prof.discord_id != uid:
                prof.discord_id = uid
                prof.save()
        except Exception:
            pass
        return user
