import jwt as pyjwt
import pytest
from fastapi import HTTPException

from app.config import get_settings
from app.security import _decode, mint_service_token
from tests.conftest import make_token


def test_service_token_matches_ticket_service_contract():
    """ticket-service's JwtVerifier does Long.valueOf(sub) — sub must be numeric."""
    settings = get_settings()
    claims = pyjwt.decode(
        mint_service_token(), settings.jwt_secret, algorithms=[settings.jwt_algorithm]
    )
    assert claims["sub"] == str(settings.ai_agent_user_id)
    assert int(claims["sub"]) == 9000
    assert claims["role"] == "AGENT"
    assert claims["exp"] - claims["iat"] == settings.service_token_ttl_seconds


def test_decode_accepts_auth_service_style_token():
    user = _decode(make_token(user_id=7, email="e@x.local", role="ADMIN"))
    assert user.id == 7
    assert user.role == "ADMIN"
    assert user.is_agent


def test_decode_rejects_bad_signature():
    bad = pyjwt.encode({"sub": "1"}, "wrong-secret-wrong-secret-wrong-secret!", algorithm="HS256")
    with pytest.raises(HTTPException):
        _decode(bad)


def test_decode_rejects_non_numeric_subject():
    settings = get_settings()
    token = pyjwt.encode(
        {"sub": "not-a-number"}, settings.jwt_secret, algorithm=settings.jwt_algorithm
    )
    with pytest.raises(HTTPException):
        _decode(token)
