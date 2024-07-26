# OpenID Connect and Python web applications

Two examples of a web application using OpenID Connect to authorize and authenticate users. Using Django 5.0.7 and Flask 3.0.3
(July 2024). These applications only support OpenID Connect Authentication Flow.

# Branches
**_main_**: OIDC Settings are loaded from environment variables (Django version) or from a json file (Flask version)

**_django-dynamic-settings_** : OIDC Settings can be managed via Django administration panel **at runtime**  (using django-constance package) and are stored in the database. Users are assigned to Django groups based on their Keycloak roles. For compatibility with other OpenID Providers, see [How it works](https://gitlab.irit.fr/gis-neocampus/datalake/oidc_auth_examples/-/blob/django-dynamic-settings/README.md?ref_type=heads#assign-groups-to-users-based-on-keycloak-roles)

**_flask-dynamic-settings_** : OIDC Settings can be managed via an admin interface at runtime. Settings are stored in environment variables. **TODO**: manage access to the admin interface, assign permissions based on Keycloak roles.


# Dependencies (django-dynamic-settings branch)
**Django example:** Depends on [mozilla-django-oidc](https://mozilla-django-oidc.readthedocs.io/en/stable/index.html) and on [django-constance](https://django-constance.readthedocs.io/en/latest/)

# Getting started (django-dynamic-settings branch)
```
git clone https://gitlab.irit.fr/gis-neocampus/datalake/neocom.git
git checkout django-dynamic-settings
```
**You must register a client in the OpenID Provider of your choice to use this application**

It's highly recomended to use Keycloak, as this project was made to only use Keycloak in the first place. 


#### **1.** Create a Python virtual environment and install dependencies

Create a Python virtual environment:
```shell
python3 -m venv [name of the virtual environment]
```
Activate the virtual environment on Windows:
```
PS:    .\[name of the virtual environment]\Scripts\Activate.ps1
CMD:    [name of the virtual environment]\Scripts\activate
```
Activate the virtual environment on Linux:
```shell
source [name of the virtual environment]/bin/activate
```
Install dependencies:
```shell
([name of the virtual environment]) > pip install -r [path to requirements.txt]
```

#### **2.** Set OIDC **default** settings in your environment variables

In this branch, OIDC settings are completely modifiable via Django's administration panel and stored in the database. The values loaded from environment variables only set the **default** values of OIDC settings.

If you don't want to load default values from environment variables, `OIDC_SETTINGS_FROM_ENV` must be set to `False` in _settings.py_. Default values can be set directly in _settings.py_ modifying the `OIDC_SETTINGS` setting.

<ins>Note</ins>: This example uses the _python-dotenv_ Python package to manage environment variables, but it isn't necessary. If _python-dotenv_ is not used this step can be skipped. Make sure to create these variables with the same names and to make them visible to Django.

Create a file named _.env_ in the same directory that contains _settings.py_. This file should look like this:
```python
# /.env
...
OIDC_ENABLED="..."
OIDC_RP_CLIENT_ID = "..."
OIDC_RP_CLIENT_SECRET = "..."
OIDC_RP_SCOPES = "..."
OIDC_RP_SIGN_ALGO = "..."
OIDC_CREATE_USER = "..."
OIDC_OP_AUTHORIZATION_ENDPOINT ="..."
OIDC_OP_TOKEN_ENDPOINT = "..."
OIDC_OP_USER_ENDPOINT = "..."
OIDC_OP_JWKS_ENDPOINT = "..." 
OIDC_OP_LOGOUT_ENDPOINT = "..."
...
```
The application doesn't support dynamic registration. Most of these informations are given by your OpenID Connect provider when registering the client.

`OIDC_CREATE_USER`: This setting determines if the app should create a local user upon first authentication. If set to `False`, only pre-existing local users will be authorized.

`OIDC_ENABLED`: This setting is not used in this project, but it may be useful. For example, this setting can determine whether a "Login with OAuth" button is displayed or not.

#### **3.** Additional settings 

**Set Django's secret key**

Read [Django's official documentation for this setting](https://docs.djangoproject.com/en/5.0/ref/settings/#secret-key).

In this project, `SECRET_KEY` is loaded from environment variables:
```python
# [yoursite]/settings.py
...
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ("DJANGO_SECRET_KEY")
...
```
Add the following to your .env file:

```python
# /.env
...
DJANGO_SECRET_KEY= "your SECRET key"
...
```
Or set the environment variable manually.


**Redirect URL after login / logout**

In _settings.py_, specify the redirect URLs after a successful login, successful logout, and failed logout.
```python
# [yoursite]/settings.py
...
LOGIN_REDIRECT_URL = ""
LOGOUT_REDIRECT_URL = ""
LOGIN_REDIRECT_URL_FAILURE = ""
...
```
<ins>Optional</ins>:

`OIDC_OP_LOGOUT_URL_METHOD`: 
As specified in [mozilla-django-oidc documentation](https://mozilla-django-oidc.readthedocs.io/en/2.0.0/installation.html#log-user-out-of-the-openid-connect-provider):
> When a user logs out, by default, mozilla-django-oidc will end the current Django session. However, the user may still have an active session with the OpenID Connect provider, in which case, the user would likely not be prompted to log back in.

> Some OpenID Connect providers support a custom (not part of OIDC spec) mechanism to end the provider’s session.

Using Keycloak, for example, implementing provider logout looks like this:

```python
# auth_app/custom.py
from django.conf import settings
def provider_logout(request):
    logout_endpoint = settings.OIDC_OP_LOGOUT_ENDPOINT
    client_id = settings.OIDC_RP_CLIENT_ID
    logout_redirect_url = settings.LOGOUT_REDIRECT_URL
    return logout_endpoint +"?post_logout_redirect_uri="+logout_redirect_url+"&client_id="+ client_id

```
`OIDC_OP_LOGOUT_URL_METHOD` is the path to the function that implements provider logout. You should set it in _settings.py_ and it should look like this:

```python
# [yoursite]/settings.py
...
OIDC_OP_LOGOUT_URL_METHOD = "app.custom.provider_logout"
...
```
This project includes provider logout using Keycloak. `OIDC_OP_LOGOUT_URL_METHOD` and `OIDC_OP_LOGOUT_ENDPOINT` can be deleted from _settings.py_ if provider logout is not implemented.

#### **4.**  Set up database

This application uses SQLite to store user data and settings.

In the directory that contains _manage.py_ run the following commands:

```shell
python manage.py makemigrations
python manage.py migrate
```

#### **5.** Run the application (after setup, this is the only command needed to run the app!):
```shell
# runs on port number 8000 by sefault
python manage.py runserver
# specify a port number:
python manage.py runserver 8006
```

#### **6.** Create groups and permissions
See [How it works](https://gitlab.irit.fr/gis-neocampus/datalake/oidc_auth_examples/-/blob/django-dynamic-settings/README.md?ref_type=heads#assign-groups-to-users-based-on-keycloak-roles)

If you want to map users to certain groups in django, you must first create the groups and assign permissions in Django's administration interface. If you don't have access to the admin panel yet, you must create a superuser:
```python
python manage.py createsuperuser
```
Then, you must access Django administration ([site url]/admin ), log in as staff (superuser or a staff user) and create groups.

# How it works

## Edit OIDC settings at runtime

The [django-constance](https://django-constance.readthedocs.io/en/latest/) package it's an easy-to-use tool to store settings that your application can modify at runtime. The only problem encoutered was making OIDC related settings dynamic, because [mozilla-django-oidc](https://mozilla-django-oidc.readthedocs.io/en/stable/installation.html#quick-start) reads them directly from _settings.py_.

To solve this problem, the authentication backend class, the middleware class and mozilla-django-oidc's view classes were derived. These child clases are the ones imported to the project instead of mozilla-django-oidc's. In each of the child classes, the _get_settings_ method is overriden to add access to Constance settings. 

For example:
```python
# auth_app/core/backends.py
...
from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from auth_app.custom import custom_get_settings

class CustomOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    @staticmethod
    def get_settings(attr, *args) :
        return custom_get_settings(attr, *args)
    ...
```
```python
# auth_app/custom.py
from django.conf import setting as defaultSettings
from constance import config as constanceSettings
from django.core.exceptions import ImproperlyConfigured
...
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
```

## Assign groups to users based on Keycloak roles
In Keycloak, roles can be assigned to users to assign permissions and access levels. To perform a role-based access control in the application we will assign users to Django groups. This way, permissions in the app can be easily managed through Django administration and permissions will be assigned to users automatically based on their Keycloak role.

To do this, we will override the `create_user` method of the mozilla-django-oidc's authentication class (see [Changing how Django users are created](https://mozilla-django-oidc.readthedocs.io/en/stable/installation.html#changing-how-django-users-are-created)). But, user roles are not stored in the `claims` object by default. So, we will override the `get_userinfo` method to also extract the user's roles from the access token. Both methods look like this:

```python
class CustomOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    ...

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
```

If your application uses other OpenID Connect provider that supports user roles, implement your own methods to create users accordingly.

Note that you must define Django groups and permissions before the application is deployed to correctly assign users.

## Generate OIDC endpoints based on issuer identifier
According to the official [OpenID Connect specification](https://openid.net/specs/openid-connect-core-1_0.html#Terminology):

> Issuer: Entity that issues a set of Claims.

> Issuer identifier: Verifiable Identifier for an Issuer. An Issuer Identifier is a case-sensitive URL using the https scheme that contains scheme, host, and optionally, port number and path components and no query or fragment components.

URLs necessary to  implement the OIDC protocol can be generated using the issuer identifier and the endpoints as specified by your identity provider. Check [Keycloak docs on endpoints](https://www.keycloak.org/docs/latest/securing_apps/#endpoints).

To do this, we could modify all endpoints when the [config-updated](https://django-constance.readthedocs.io/en/latest/#signals) signal is received. Unfortunately, [this issue](https://github.com/jazzband/django-constance/issues/515) is preventing this method to work.

Another solution is to derive the Constance admin class and register it in our application. Overriding the `changelist_view` view method allows the app to detect changes in the issuer field and save the new urls after the form is saved (using signals, the new URLs were set when saving the form which causes the issue)

```python
# auth_app/admin.py
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
```
