# OpenID Connect and Python web applications

Two examples of a web application using OpenID Connect to authorize and authenticate users. Using Django 5.0.7 and Flask 3.0.3
(July 2024) These applications only support OpenID Connect Authentication Flow.

# Branches
**_main_**: OIDC Settings are loaded from environment variables (Django version) or from a json file (Flask version)

**_django-dynamic-settings_** : OIDC Settings can be managed via Django administration panel **at runtime**  (using django-constance package). Users are assigned to Django groups based on their Keycloak roles. For compatibility with other OpenID Providers, see [How it works](https://gitlab.irit.fr/gis-neocampus/datalake/oidc_auth_examples/-/blob/django-dynamic-settings/README.md?ref_type=heads#assign-groups-to-users-based-on-keycloak-roles)

**_flask-dynamic-settings_** : [Not finished]

# Dependencies (flask-dynamic-settings branch)
**Flask example:** Depends on [requests-oauthlib](https://requests-oauthlib.readthedocs.io/en/latest/), [Flask-Admin](https://flask-admin.readthedocs.io/en/latest/), [Flask-Login](https://flask-login.readthedocs.io/en/latest/), [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/), [Pyjwt](https://pyjwt.readthedocs.io/en/stable/)


# Getting started (flask-dynamic-settings branch)
```
git clone https://gitlab.irit.fr/gis-neocampus/datalake/neocom.git
git checkout flask-dynamic-settings
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
#### **2.** Set OIDC settings in your environment variables

Create a file named _.env_ in the same directory that contains _settings.py_. This file should look like this:

```python
# /.env
...
OIDC_CLIENT_ID = "..."
OIDC_CLIENT_SECRET = "..."
OIDC_ISSUER = "..."
OIDC_SCOPE = "..."
OIDC_SIGNING_ALGORITHMS = "..."
...
```
The application doesn't support dynamic registration. Most of these informations are given by your OpenID Connect provider when registering the client.

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
Add the following to your .env file:

```python
# /.env
...
FLASK_SECRET_KEY= "your SECRET key"
...
```
Else, set the environment variable manually.

**Provider logout**

The flask-login's logout method only clears cookies and the user's current session. However, as specified in the [Django example's Getting started section](https://gitlab.irit.fr/gis-neocampus/datalake/oidc_auth_examples#django-example):
> [...] the user may still have an active session with the OpenID Connect provider, in which case, the user would likely not be prompted to log back in.

> Some OpenID Connect providers support a custom (not part of OIDC spec) mechanism to end the provider’s session.

When using Keycoak, a provider logout view method may look like this:
```python
...
@app.route("/provider_logout")
    def provider_logout():
        post_logout_redirect_uri = url_for('local_logout')
        response = redirect(oidc_settings.logout_endpoint + '?post_logout_redirect_uri=' 
                            + post_logout_redirect_uri + '&client_id=' + oidc_settings.client_id, code=302)
        return response

    @app.route("/local_logout")
    def local_logout():
        logout_user()
        return redirect(url_for('index'))
```
Note that after the provider logout, the user is redirected to the local logout view. This order is important when using Keycloak. If Keycloak is configured to prompt the user to confirm their intent to log out, it may display a 'Back' button during the process. If the user clicks the 'Back' button, they should still be logged in because they didn't confirm the logout. However, if the local logout is executed before the provider logout, clicking the 'Back' button will log the user out locally in the application.



#### **5.** Run the application

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