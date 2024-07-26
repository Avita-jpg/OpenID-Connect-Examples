from base64 import b64decode
import json
from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from django.contrib.auth.models import Group
from auth_app.custom import custom_get_settings

class CustomOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    @staticmethod
    def get_settings(attr, *args) :
        return custom_get_settings(attr, *args)
    
    # adds roles in user info dictionary
    def get_userinfo(self, access_token, id_token, payload):
        user_info = super().get_userinfo(access_token, id_token, payload)

        # decode access_token without verification
        payload_data = access_token.split(".")[1]
        payload_data_decoded = b64decode(payload_data)
        payload = json.loads(payload_data_decoded.decode("utf-8"))

        # add roles to user_info object
        user_info["roles"] = payload["realm_access"]["roles"]

        return user_info

    # assigns users to groups based on keycloak roles 
    def create_user(self, claims):
        user = super().create_user(claims)
        # retreive roles extracted in get_userinfo()
        keycloak_roles = claims.get("roles")
        # parse roles and add user to groups
        for role in keycloak_roles:
            try: 
                group = Group.objects.get(name=role)
                user.groups.add(group)
                # staff users must have a keycloak role like "[role]-admin"
                if role.split("-")[-1] == 'admin':
                    user.is_staff = True
                user.save()
            except Group.DoesNotExist:
                print(role + ' group does not exist') 
        return user
