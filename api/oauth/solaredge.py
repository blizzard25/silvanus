# oauth/solaredge.py
import requests
from api.oauth.manager import OAuthProvider, register_provider

CLIENT_ID = "YOUR_SOLAREDGE_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
AUTH_URL = "https://solaredge.com/oauth/authorize"
TOKEN_URL = "https://solaredge.com/oauth/token"

@register_provider("solaredge")
class SolarEdgeOAuth(OAuthProvider):
    def get_auth_url(self, redirect_uri: str) -> str:
        return f"{AUTH_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={redirect_uri}&scope=read_site"

    def exchange_code(self, code: str, redirect_uri: str):
        response = requests.post(TOKEN_URL, data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        })
        response.raise_for_status()
        return response.json()
