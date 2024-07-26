from mozilla_django_oidc.middleware import SessionRefresh
from auth_app.custom import custom_get_settings

class CustomOIDCSessionRefresh(SessionRefresh):
    @staticmethod
    def get_settings(attr, *args) :
        return custom_get_settings(attr, *args)