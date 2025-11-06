from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        import accounts.signals  # noqa
        from django.db.models.signals import post_save
        from django.contrib.auth.models import User
        from .models import Profile

        def ensure_profile(sender, instance, created, **kwargs):
            if created:
                Profile.objects.get_or_create(user=instance)
        post_save.connect(ensure_profile, sender=User)
