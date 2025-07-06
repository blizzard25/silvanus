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
    def get_auth_url(self, redirect_uri: str) -> str:
        pass

    @abstractmethod
    def exchange_code(self, code: str, redirect_uri: str) -> Dict:
        pass
