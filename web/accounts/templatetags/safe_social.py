from django import template
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from allauth.socialaccount.templatetags import socialaccount as allauth_social_tags

register = template.Library()


@register.simple_tag(takes_context=True)
def safe_provider_login_url(context, provider, **kwargs):
    """
    Wrap allauth's provider_login_url so that if the SocialApp
    is missing or duplicated we just return "" instead of raising.
    """
    try:
        return allauth_social_tags.provider_login_url(context, provider, **kwargs)
    except (ObjectDoesNotExist, MultipleObjectsReturned):
        return ""
