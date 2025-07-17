# oauth/manager.py
from abc import ABC, abstractmethod
from typing import Dict

OAUTH_PROVIDERS = {}

def register_provider(name):
    def wrapper(cls):
        OAUTH_PROVIDERS[name] = cls()
        return cls
    return wrapper

class OAuthProvider(ABC):
    @abstractmethod
    def get_auth_url(self, redirect_uri: str, user_id: str = None) -> Dict[str, str]:
        """
        Generate OAuth2.0 authorization URL with security parameters.
        
        Args:
            redirect_uri: OAuth redirect URI
            user_id: Optional user identifier for session tracking
            
        Returns:
            Dict containing auth_url, state, and session_key
        """
        pass

    @abstractmethod
    def exchange_code(self, code: str, state: str, redirect_uri: str = None, session_key: str = None) -> Dict:
        """
        Exchange authorization code for access tokens with security validation.
        
        Args:
            code: OAuth authorization code
            state: State parameter for CSRF protection
            redirect_uri: OAuth redirect URI
            session_key: Session key for PKCE validation
            
        Returns:
            Dict containing access_token, refresh_token, expires_in, etc.
        """
        pass
