from flask import Flask, redirect, render_template, request, url_for
from flask_oidc import OpenIDConnect
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config.update({
    'OIDC_CLIENT_SECRETS': 'client_secrets.json',
    'SECRET_KEY': os.environ("FLASK_SECRET_KEY"),
    'OIDC_LOGOUT_ENDPOINT': 'https://neosso.univ-tlse3.fr/realms/neOCampus/protocol/openid-connect/logout',
    'APPLICATION_ROOT': '/'
})

oidc = OpenIDConnect(app)

@app.route('/')
def menu():
    if (oidc.user_loggedin) :
        return render_template('index.html', state='loggedin', email=oidc.user_getfield('email'))
    return render_template('index.html')

@app.route('/login')
@oidc.require_login
def login():
    return render_template('index.html')

@app.route('/provider_logout')
def provider_logout():
    post_logout_redirect_uri = url_for('local_logout', _external=True)
    response = redirect(app.config["OIDC_LOGOUT_ENDPOINT"] + '?post_logout_redirect_uri=' 
                        + post_logout_redirect_uri + '&client_id=' + app.config["OIDC_CLIENT_ID"], code=302)
    return response

@app.route('/local_logout')
def local_logout():
    return redirect(url_for("oidc_auth.logout"))

if __name__ == '__main__':
    app.run(debug=True)