import time
from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException, Request, status

from app.config import get_settings


@dataclass(frozen=True)
class AuthUser:
    id: int
    email: str
    role: str
    token: str
    """Raw bearer token, passed through to ticket-service on the user's behalf."""

    @property
    def is_agent(self) -> bool:
        return self.role in ("AGENT", "ADMIN")


def _decode(token: str) -> AuthUser:
    settings = get_settings()
    try:
        claims = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        # auth-service issues numeric subjects (ticket-service's JwtVerifier
        # relies on the same contract via Long.valueOf).
        user_id = int(claims["sub"])
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token") from exc
    return AuthUser(
        id=user_id,
        email=claims.get("email", ""),
        role=claims.get("role", "REQUESTER"),
        token=token,
    )


async def verify_jwt(request: Request) -> AuthUser:
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token")
    return _decode(header.removeprefix("Bearer "))


async def require_agent(user: AuthUser = Depends(verify_jwt)) -> AuthUser:
    if not user.is_agent:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "AGENT or ADMIN role required")
    return user


def mint_service_token() -> str:
    """Short-lived AGENT JWT for the seeded ai@helpdesk.local service account (id 9000)."""
    settings = get_settings()
    now = int(time.time())
    return jwt.encode(
        {
            "sub": str(settings.ai_agent_user_id),
            "email": settings.ai_agent_email,
            "role": "AGENT",
            "iat": now,
            "exp": now + settings.service_token_ttl_seconds,
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
