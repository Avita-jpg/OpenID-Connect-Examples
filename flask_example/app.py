"""
Based on: https://requests-oauthlib.readthedocs.io/en/latest/examples/real_world_example.html
Using pyjwt to add oidc authentication : https://pyjwt.readthedocs.io/en/stable/usage.html#oidc-login-flow (verify id token)

"""
import base64
import os
import jwt
import jwt.api_jwt
from flask import Flask, abort, flash, render_template, request, redirect, session, url_for
from flask.views import View
from requests_oauthlib import OAuth2Session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user,\
    current_user
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from settings import OIDCSettings

app = Flask(__name__)
SECRET_KEY = os.environ("FLASK_SECRET_KEY")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

# redirect uri to go to after authorization
app.config['REDIRECT_URI'] = "http://localhost:5000/callback"

# set bootswatch theme
app.config['FLASK_ADMIN_SWATCH'] = 'flatly'

# initialize custom class OIDCSettings to access OpenID Connect settings stored in environment variables
oidc_settings = OIDCSettings(".env")

@app.route("/")
def index():
    return render_template("index.html")

class LoginView(View):
    # redirect user to the OIDC Provider
    @app.route("/authorize")
    def authorize():
        if not current_user.is_anonymous:
            return redirect(url_for('index'))
        
        oauth = OAuth2Session(oidc_settings.client_id, redirect_uri=app.config["REDIRECT_URI"], scope=oidc_settings.scopes.split(" "))
        # TODO: add nonce to prevent replay attacks
        authorization_url, state = oauth.authorization_url(oidc_settings.authorization_base_endpoint)

        session['oauth_state'] = state
        return redirect(authorization_url)
    
    # # After receiving authorization token: Retrieve access token and verify jwt
    # https://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation
    @app.route("/callback", methods=['GET'])
    def authenticate():
        if not current_user.is_anonymous:
            return redirect(url_for('index'))

        #if there was an error in the authorization request
        if 'error' in request.args:
            for k, v in request.args.items():
                if k.startswith('error'):
                    flash(f'{k}: {v}')
            return redirect(url_for('index'))
        
        # make sure that the state parameter matches the one we created in the
        # authorization request
        if request.args['state'] != session.get('oauth_state'):
            abort(401)

        # make sure that the authorization code is present
        if 'code' not in request.args:
            abort(401)

        # fetch token on token endpoint
        oauth = OAuth2Session(oidc_settings.client_id, state=session['oauth_state'], redirect_uri=app.config["REDIRECT_URI"], scope=oidc_settings.scopes.split(" "))
        token = oauth.fetch_token(oidc_settings.token_endpoint, client_secret=oidc_settings.client_secret, authorization_response=request.url.replace('http://', 'https://'))

        # https://openid.net/specs/openid-connect-core-1_0.html#TokenResponse
        access_token = token['access_token']
        id_token = token['id_token']

        # get signing_key from id_token
        jwks_client = jwt.PyJWKClient(oidc_settings.jwks_endpoint)
        signing_key = jwks_client.get_signing_key_from_jwt(id_token)

        # TODO: verify nonce
        # now, decode_complete to get payload + header
        # this also verifies claims in id token
        data = jwt.api_jwt.decode_complete(
            id_token,
            key=signing_key.key,
            algorithms=oidc_settings.signing_algos.split(" "),
            audience=oidc_settings.client_id,
            issuer=oidc_settings.issuer,
            verify_signature=True
        )
        payload, header = data["payload"], data["header"]

        # verify at_hash
        alg_obj = jwt.get_algorithm_by_name(header["alg"])
        digest = alg_obj.compute_hash_digest(access_token.encode('ascii'))
        at_hash = base64.urlsafe_b64encode(digest[: (len(digest) // 2)]).decode().split("==")[0]

        assert at_hash == payload["at_hash"] #TODO: raise exception, not assert

        session['oauth_token'] = token
        return redirect(url_for('.login'))

    # request the identity provider to forget the user session so user must authenticate next time
    # then redirect to local logout
    @app.route("/provider_logout")
    def provider_logout():
        post_logout_redirect_uri = url_for('local_logout', _external=True)
        response = redirect(oidc_settings.logout_endpoint + '?post_logout_redirect_uri=' 
                            + post_logout_redirect_uri + '&client_id=' + oidc_settings.client_id, code=302)
        return response

    # forget local user session
    @app.route("/local_logout")
    def local_logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route("/login", methods=["GET"])
    def login():
        oauth = OAuth2Session(oidc_settings.client_id, token=session['oauth_token'])
        # get user info from provider
        userinfo_data = oauth.get(oidc_settings.userinfo_endpoint).json()
        
        # find or create the user in the database
        user = db.session.scalar(db.select(User).where(User.email == userinfo_data['email']))
        if user is None: # TODO add autocreate
            user = User(email=userinfo_data['email'], username=userinfo_data['preferred_username'])
            db.session.add(user)
            db.session.commit()
        
        # log the user in
        login_user(user)
        return redirect(url_for('index'))


# to store users
db = SQLAlchemy(app)

# User model in database
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(64), nullable=True)

# login manager instance
login = LoginManager(app)
login.login_view = 'LoginView.authorize'

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

# create database tables
with app.app_context():
    db.create_all()

# custom admin view to modify oidc settings
class OAuthSettingsView(BaseView):
    @expose('/', methods=['GET'])
    def index(self):
        return self.render('oauth-config.html', settings=oidc_settings)
    
    @expose('/', methods=['POST'])
    def config(self):
        oidc_settings.set_settings(request.form.get("client_id"),
                                    request.form.get("client_secret"), 
                                    request.form.get("issuer"), 
                                    request.form.get("scopes"), 
                                    request.form.get("signing_algos"))
        flash('OAuth settings saved!') #TODO: fix: this is being shown twice
        return redirect(url_for("oauth-settings.index"))

# create admin views
# TODO: Important: limit access to admin configuration
admin = Admin(app, name='App administration', template_mode='bootstrap3')
# user model view to manage app users
admin.add_view(ModelView(User, db.session))
# oidc settings view
admin.add_view(OAuthSettingsView(name='OAuth settings', endpoint='oauth-settings'))

if __name__ == "__main__":
    # TODO: WARNING: must use HTTPS (but it doesn't work using https right now)
    # This allows us to use a plain HTTP callback
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"
    app.run(debug=True)
