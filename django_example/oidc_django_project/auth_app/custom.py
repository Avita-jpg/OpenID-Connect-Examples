from django.conf import settings as defaultSettings
from constance import config as constanceSettings
from django.core.exceptions import ImproperlyConfigured

# helper functions

# as specified in: https://mozilla-django-oidc.readthedocs.io/en/2.0.0/installation.html#log-user-out-of-the-openid-connect-provider
def provider_logout(request):
    logout_endpoint = custom_get_settings("OIDC_OP_LOGOUT_ENDPOINT")
    client_id = custom_get_settings("OIDC_RP_CLIENT_ID")
    return logout_endpoint +"?post_logout_redirect_uri="+ request.build_absolute_uri("/")+"&client_id="+ client_id

# custom get_settings: looks for settings in Constance instance if OIDC related, else gets them from Django settings file
def custom_get_settings(attr, *args) :
    if attr in defaultSettings.OIDC_SETTINGS: 
        source = constanceSettings
    else:
        source = defaultSettings
    try:
        if args:
            return getattr(source, attr, args[0])
        return getattr(source, attr)
    except AttributeError:
        raise ImproperlyConfigured("Setting {0} not found".format(attr))
