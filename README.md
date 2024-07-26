# OpenID Connect and Python web applications

Two examples of a web application using OpenID Connect to authorize and authenticate users. Using Django 5.0.7 and Flask 3.0.3
(July 2024). These applications only support OpenID Connect Authentication Flow.

# Branches
**_main_**: OIDC Settings are loaded from environment variables (Django version) or from a json file (Flask version)

**_django-dynamic-settings_** : OIDC Settings can be managed via Django administration panel **at runtime**  (using django-constance package) and are stored in the database. Users are assigned to Django groups based on their Keycloak roles. For compatibility with other OpenID Providers, see [How it works](https://gitlab.irit.fr/gis-neocampus/datalake/oidc_auth_examples/-/blob/django-dynamic-settings/README.md?ref_type=heads#assign-groups-to-users-based-on-keycloak-roles)

**_flask-dynamic-settings_** : OIDC Settings can be managed via an admin interface at runtime. Settings are stored in environment variables. **TODO**: manage access to the admin interface, assign permissions based on Keycloak roles.

# Dependencies (Main branch)
**Django example:** Depends on [mozilla-django-oidc](https://mozilla-django-oidc.readthedocs.io/en/stable/index.html)

**Flask example:** Depends on [Flask-OIDC](https://flask-oidc.readthedocs.io/en/latest/)

# Getting started (Main branch)
```
git clone https://gitlab.irit.fr/gis-neocampus/datalake/neocom.git
git checkout main
```
**You must register a client in the OpenID Provider of your choice to use this application**

It's highly recomended to use Keycloak, as this project was made to only use Keycloak in the first place. 


## For both Django and Flask examples
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

## Django example
#### **2.** Set OIDC settings in your environment variables

<ins>Note</ins>: This example uses the _python-dotenv_ Python package to manage environment variables, but it isn't necessary. If _python-dotenv_ is not used this step can be skipped. Make sure to create these variables with the same names and to make them visible to Django.

Create a file named _.env_ in the same directory that contains _settings.py_. This file should look like this:
```python
# /.env
...
OIDC_RP_CLIENT_ID = "..."
OIDC_RP_CLIENT_SECRET = "..."
OIDC_RP_SCOPES = "..."
OIDC_RP_SIGN_ALGO = "..."
OIDC_OP_AUTHORIZATION_ENDPOINT ="..."
OIDC_OP_TOKEN_ENDPOINT = "..."
OIDC_OP_USER_ENDPOINT = "..."
OIDC_OP_JWKS_ENDPOINT = "..." 
OIDC_OP_LOGOUT_ENDPOINT = "..."
...
```
The application doesn't support dynamic registration. Most of these informations are given by your OpenID Connect provider when registering the client.

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

`OIDC_CREATE_USER`: This setting determines if the app should create a local user upon first authentication. If set to `False`, only pre-existing local users will be authorized. By default, this setting is set to `True`. To change it, add it to your environment variables. 

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

This application uses SQLite to store user data.

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
## Flask example
#### **2.** Set OIDC settings in _client\_secrets.json_

Create a file called _client\_secrets.json_. This is where you are going to manually enter all the informations required to enable OIDC authentication. Most of these informations are given by your OpenID Connect provider when registering the client. The application doesn't support dynamic registration. 

The file should look like this:
```json
{
    "web" : {
        "client_id" : "...", 
        "client_secret": "...",
        "auth_uri": "...",
        "token_uri": "...",
        "userinfo_uri": "...",
        "issuer": "...",
        "redirect_uris": ["..."]
    }
}
```
Enter the path to this file in the `OIDC_CLIENT_SECRETS` field of the app's configuration:

```python
# app.py
... # imports
app = Flask(__name__)
app.config.update({
    ...
    'OIDC_CLIENT_SECRETS': '[path]/client_secrets.json',
    ...
})
...
```

#### **3**. Additional settings

**Set Flask's secret key**

Read [Flask's official documentation for this setting](https://flask.palletsprojects.com/en/3.0.x/config/#SECRET_KEY).

In this project, `SECRET_KEY` is loaded from environment variables:
```python
# app.py
...
app.config.update({
    ...
    SECRET_KEY = os.environ("FLASK_SECRET_KEY")
    ...
})
...
```
<ins>Note</ins>: This example uses the _python-dotenv_ Python package to manage environment variables, but it isn't necessary. If your app uses _python-dotenv_ add the following to your .env file:

```python
# /.env
...
FLASK_SECRET_KEY= "your SECRET key"
...
```
Else, set the environment variable manually.

**Provider logout**

The flask-oidc package's logout view, as described in the [documentation](https://flask-oidc.readthedocs.io/en/latest/_source/flask_oidc.html#flask_oidc.OpenIDConnect.logout), only clears cookies and the user's current session. However, as specified in the [Django example's Getting started section](https://gitlab.irit.fr/gis-neocampus/datalake/oidc_auth_examples#django-example):
> [...] the user may still have an active session with the OpenID Connect provider, in which case, the user would likely not be prompted to log back in.

> Some OpenID Connect providers support a custom (not part of OIDC spec) mechanism to end the provider’s session.

When using Keycoak, a provider logout view method may look like this:
```python
...
@app.route('/provider_logout')
def provider_logout():
    post_logout_redirect_uri = url_for('local_logout', _external=True)
    response = redirect(app.config["OIDC_LOGOUT_ENDPOINT"] + '?post_logout_redirect_uri=' 
                        + post_logout_redirect_uri + '&client_id=' + app.config["OIDC_CLIENT_ID"], code=302)
    return response

@app.route('/local_logout')
def local_logout():
    return redirect(url_for("oidc_auth.logout"))
...
```
Note that after the provider logout, the user is redirected to the local logout view. This order is important when using Keycloak. If Keycloak is configured to prompt the user to confirm their intent to log out, it may display a 'Back' button during the process. If the user clicks the 'Back' button, they should still be logged in because they didn't confirm the logout. However, if the local logout is executed before the provider logout, clicking the 'Back' button will log the user out locally in the application.

This project implements provider logout, to use it define the value of the `OIDC_LOGOUT_ENDPOINT` key in the app's configuation.

#### **4.** Run the application

```shell
# default port number: 5000
flask run
# specify a port number:
flask run --port 8006
```
An alternative way to run the application is writing the following code at the end of _app.py_.
```shell
# app.py
...
if __name__ == '__main__':
    app.run(debug=True, port=8006)
```
Then:
```shell
python app.py
```
