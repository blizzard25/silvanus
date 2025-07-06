# oauth/github.py
import os
import requests
from urllib.parse import urlencode
from typing import Optional

from api.oauth.manager import OAuthProvider, register_provider

CLIENT_ID = "GITHUB_CLIENT_ID"
CLIENT_SECRET = "GITHUB_CLIENT_SECRET"
DEFAULT_REDIRECT_URI = "https://silvanus-a4nt.onrender.com/oauth/callback/github"
AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
TOKEN_URL = "https://github.com/login/oauth/access_token"

@register_provider("github")
class GitHubOAuthProvider(OAuthProvider):
    def get_auth_url(self, redirect_uri: Optional[str] = None) -> str:
        redirect_uri = redirect_uri or DEFAULT_REDIRECT_URI
        params = {
            "client_id": CLIENT_ID,
            "redirect_uri": redirect_uri,
            "scope": "read:user user:email",
        }
        return f"{AUTHORIZE_URL}?{urlencode(params)}"

    def exchange_code(self, code: str, redirect_uri: str = DEFAULT_REDIRECT_URI) -> dict:
        redirect_uri = redirect_uri or DEFAULT_REDIRECT_URI

        data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "redirect_uri": redirect_uri,
        }

        headers = {"Accept": "application/json"}
        response = requests.post(TOKEN_URL, data=data, headers=headers)
        response.raise_for_status()

        return response.json()