from django.contrib import admin
from constance.admin import Config, ConstanceAdmin, get_values
from constance import config

admin.site.unregister([Config])

class CustomConstanceAdmin(ConstanceAdmin):
    
    def changelist_view(self, request, extra_context=None):
        """ 
        check if OIDC_ISSUER_URL has changed and updates it AFTER the form is saved
        """
        old_issuer = get_values()["OIDC_ISSUER_URL"]
        if request.method == 'POST' and request.user.has_perm('constance.change_config'):
           response = super().changelist_view(request)
        else: 
            return super().changelist_view(request)
        new_issuer = get_values()["OIDC_ISSUER_URL"]
        if old_issuer != new_issuer:
            set_urls(new_issuer)
        return response

def set_urls(new_issuer):
    setattr(config, 'OIDC_OP_AUTHORIZATION_ENDPOINT', '{base}/protocol/openid-connect/auth'.format(base=new_issuer))
    setattr(config, 'OIDC_OP_TOKEN_ENDPOINT', '{base}/protocol/openid-connect/token'.format(base=new_issuer))
    setattr(config, 'OIDC_OP_USER_ENDPOINT', '{base}/protocol/openid-connect/userinfo'.format(base=new_issuer))
    setattr(config, 'OIDC_OP_JWKS_ENDPOINT', '{base}/protocol/openid-connect/certs'.format(base=new_issuer))
    setattr(config, 'OIDC_OP_LOGOUT_ENDPOINT', '{base}/protocol/openid-connect/logout'.format(base=new_issuer))

admin.site.register([Config], CustomConstanceAdmin)