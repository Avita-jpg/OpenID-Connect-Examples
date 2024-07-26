from django.conf import settings

# helper functions
# as specified in: https://mozilla-django-oidc.readthedocs.io/en/2.0.0/installation.html#log-user-out-of-the-openid-connect-provider
def provider_logout(request):
    logout_endpoint = settings.OIDC_OP_LOGOUT_ENDPOINT
    client_id = settings.OIDC_RP_CLIENT_ID
    logout_redirect_url = settings.LOGOUT_REDIRECT_URL
    return logout_endpoint +"?post_logout_redirect_uri="+logout_redirect_url+"&client_id="+ client_id
