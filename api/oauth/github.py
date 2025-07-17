# oauth/github.py
import os
import requests
import secrets
import hashlib
import base64
from urllib.parse import urlencode
from typing import Optional, Dict
from dotenv import load_dotenv

from api.oauth.manager import OAuthProvider, register_provider

load_dotenv()

CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "Ov23liUpkKdBsXGV3K1p")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
DEFAULT_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI", "https://silvanus-a4nt.onrender.com/oauth/callback/github")
AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
TOKEN_URL = "https://github.com/login/oauth/access_token"

if not CLIENT_SECRET:
    raise ValueError("GITHUB_CLIENT_SECRET environment variable is required")

@register_provider("github")
class GitHubOAuthProvider(OAuthProvider):
    def __init__(self):
        self._state_storage = {}  # In production, use Redis or database
        self._pkce_storage = {}   # In production, use Redis or database
    
    def _generate_pkce_pair(self) -> tuple[str, str]:
        """Generate PKCE code verifier and challenge"""
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')
        return code_verifier, code_challenge
    
    def _generate_state(self) -> str:
        """Generate cryptographically secure state parameter"""
        return secrets.token_urlsafe(32)
    
    def get_auth_url(self, redirect_uri: Optional[str] = None, user_id: Optional[str] = None) -> Dict[str, str]:
        """Generate authorization URL with PKCE and state parameters"""
        redirect_uri = redirect_uri or DEFAULT_REDIRECT_URI
        
        code_verifier, code_challenge = self._generate_pkce_pair()
        
        state = self._generate_state()
        
        session_key = user_id or state
        self._pkce_storage[session_key] = code_verifier
        self._state_storage[session_key] = state
        
        params = {
            "client_id": CLIENT_ID,
            "redirect_uri": redirect_uri,
            "scope": "read:user user:email",
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "response_type": "code"
        }
        
        auth_url = f"{AUTHORIZE_URL}?{urlencode(params)}"
        
        return {
            "auth_url": auth_url,
            "state": state,
            "session_key": session_key
        }

    def exchange_code(self, code: str, state: str, redirect_uri: str = DEFAULT_REDIRECT_URI, session_key: Optional[str] = None) -> dict:
        """Exchange authorization code for tokens with PKCE validation"""
        redirect_uri = redirect_uri or DEFAULT_REDIRECT_URI
        
        if not session_key:
            session_key = state
            
        stored_state = self._state_storage.get(session_key)
        if not stored_state or stored_state != state:
            raise ValueError("Invalid or expired state parameter - possible CSRF attack")
        
        code_verifier = self._pkce_storage.get(session_key)
        if not code_verifier:
            raise ValueError("Invalid or expired PKCE parameters")
        
        data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "redirect_uri": redirect_uri,
            "code_verifier": code_verifier
        }

        headers = {"Accept": "application/json"}
        
        try:
            response = requests.post(TOKEN_URL, data=data, headers=headers)
            response.raise_for_status()
            
            token_data = response.json()
            
            if "error" in token_data:
                error_description = token_data.get("error_description", "Unknown OAuth error")
                raise ValueError(f"OAuth2.0 error: {token_data['error']} - {error_description}")
            
            self._pkce_storage.pop(session_key, None)
            self._state_storage.pop(session_key, None)
            
            return token_data
            
        except requests.RequestException as e:
            raise ValueError(f"Token exchange failed: {str(e)}")
        except Exception as e:
            self._pkce_storage.pop(session_key, None)
            self._state_storage.pop(session_key, None)
            raise
