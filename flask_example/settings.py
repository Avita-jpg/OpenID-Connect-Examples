import dotenv
import os

class OIDCSettings():
    def __init__(self, dotenv_path) -> None:
        self.dotenv_path = dotenv_path
        #TODO case: dotenvfile not correctly defined
        self.__load_settings()

    def __load_settings(self):
        dotenv.load_dotenv(self.dotenv_path, override=True)
        self.client_id = os.getenv("OIDC_CLIENT_ID")
        self.client_secret = os.getenv("OIDC_CLIENT_SECRET")
        self.scopes = os.getenv("OIDC_SCOPE")
        self.issuer= os.getenv("OIDC_ISSUER")
        self.signing_algos = os.getenv("OIDC_SIGNING_ALGORITHMS")
        self.__generate_endpoints()

    def __generate_endpoints(self):
        base_url = self.issuer+"/protocol/openid-connect"
        self.authorization_base_endpoint = base_url+"/auth"
        self.token_endpoint = base_url+"/token"
        self.userinfo_endpoint = base_url+"/userinfo"
        self.jwks_endpoint = base_url+"/certs"
        self.logout_endpoint = base_url+"/logout"

    def set_settings(self, client_id, client_secret, issuer, scopes, signing_algorithms="RS256"):
        dotenv.set_key(self.dotenv_path, "OIDC_CLIENT_ID", client_id)
        dotenv.set_key(self.dotenv_path, "OIDC_CLIENT_SECRET", client_secret)
        dotenv.set_key(self.dotenv_path, "OIDC_ISSUER", issuer)
        dotenv.set_key(self.dotenv_path, "OIDC_SCOPE", scopes)
        dotenv.set_key(self.dotenv_path, "OIDC_SIGNING_ALGORITHMS", signing_algorithms)
        self.__load_settings()
        
