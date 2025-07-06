# api/models/token.py
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from api.database import Base

class OAuthToken(Base):
    __tablename__ = "oauth_tokens"

    id = Column(Integer, primary_key=True, index=True)
    wallet_address = Column(String, index=True)
    provider = Column(String, index=True)
    access_token = Column(String)
    refresh_token = Column(String)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
