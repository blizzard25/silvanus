"""
Pydantic models for Silvanus API request/response data structures.
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator
from web3 import Web3


class ActivitySubmission(BaseModel):
    """Model for submitting green energy activities."""

    wallet_address: str = Field(..., description="Ethereum wallet address")
    activity_type: str = Field(..., description="Type of green activity")
    value: float = Field(
        ..., ge=0.0, le=10000.0, description="Activity value in kWh (0-10000)"
    )
    details: Dict[str, Any] = Field(
        default_factory=dict, description="Additional activity details"
    )

    @field_validator("wallet_address")
    @classmethod
    def validate_wallet_address(cls, v: str) -> str:
        if not v:
            raise ValueError("Wallet address is required")

        address = v.lower()
        if address.startswith("0x"):
            address = address[2:]

        if not re.match(r"^[0-9a-f]{40}$", address):
            raise ValueError("Invalid Ethereum wallet address format")

        normalized_address = "0x" + address if not v.startswith("0x") else v.lower()
        return Web3.to_checksum_address(normalized_address)

    @field_validator("activity_type")
    @classmethod
    def validate_activity_type(cls, v: str) -> str:
        valid_types = {
            "solar_export",
            "ev_charging",
            "energy_saving",
            "carbon_offset",
            "renewable_energy",
            "green_transport",
            "waste_reduction",
        }
        if v not in valid_types:
            raise ValueError(
                f'Invalid activity type. Must be one of: {", ".join(valid_types)}'
            )
        return v

    @field_validator("value")
    @classmethod
    def validate_value(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Activity value must be non-negative")
        if v > 10000:
            raise ValueError("Activity value cannot exceed 10000 kWh")
        return round(float(v), 2)


class ActivityResponse(BaseModel):
    """Response model for activity submission."""

    txHash: str = Field(..., description="Blockchain transaction hash")
    status: str = Field(..., description="Transaction status (confirmed/pending)")


class ActivityType(BaseModel):
    """Model for supported activity types."""

    type: str = Field(..., description="Activity type identifier")
    description: str = Field(..., description="Human-readable description")
    expectedDetails: List[str] = Field(..., description="Expected detail fields")


class OAuthLoginResponse(BaseModel):
    """Response model for OAuth login initiation."""

    auth_url: str = Field(..., description="OAuth authorization URL")
    state: str = Field(..., description="OAuth state parameter")
    session_key: str = Field(..., description="Session key for PKCE")
    provider: str = Field(..., description="OAuth provider name")


class OAuthCallbackResponse(BaseModel):
    """Response model for OAuth callback processing."""

    message: str = Field(..., description="Success message")
    provider: str = Field(..., description="OAuth provider name")
    wallet_address: str = Field(..., description="Associated wallet address")
    token_id: int = Field(..., description="Token database ID")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    expires_at: str = Field(..., description="Token expiration timestamp")
    has_refresh_token: bool = Field(
        ..., description="Whether refresh token is available"
    )


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str = Field(default="ok", description="Health status")


class ErrorResponse(BaseModel):
    """Standard error response model."""

    detail: str = Field(..., description="Error message")
    status_code: Optional[int] = Field(None, description="HTTP status code")
