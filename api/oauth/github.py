# oauth/github.py
import requests
from api.oauth.manager import OAuthProvider, register_provider

CLIENT_ID = "Ov23liUpkKdBsXGV3K1p"
CLIENT_SECRET = "833c113479be3858e5f7e2cad7dde83bb1ba03b4"
AUTH_URL = "https://github.com/login/oauth/authorize"
TOKEN_URL = "https://github.com/login/oauth/access_token"

@register_provider("github")
class GitHubOAuth(OAuthProvider):
    def get_auth_url(self, redirect_uri: str) -> str:
        return f"{AUTH_URL}?client_id={CLIENT_ID}&redirect_uri={redirect_uri}&scope=read:user"

    def exchange_code(self, code: str, redirect_uri: str):
        headers = {'Accept': 'application/json'}
        response = requests.post(TOKEN_URL, data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "redirect_uri": redirect_uri,
        }, headers=headers)
        response.raise_for_status()
        return response.json()
