from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time

from fastapi import APIRouter, Cookie, HTTPException, Response
from pydantic import BaseModel

from app.config import get_settings
from app.models.schemas import APIResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# Demo users — no database needed. Passwords come from env
# (ADMIN_PASSWORD / DEMO_PASSWORD) with local-dev defaults.
def _get_users() -> dict:
    settings = get_settings()
    return {
        "admin": {"password": settings.admin_password, "role": "admin", "name": "Admin"},
        "demo": {"password": settings.demo_password, "role": "viewer", "name": "Demo User"},
    }

SESSION_MAX_AGE = 60 * 60 * 24  # 24 hours


class LoginRequest(BaseModel):
    username: str
    password: str


def _sign_token(payload: dict) -> str:
    """Create a signed session token (HMAC + JSON, not a full JWT)."""
    settings = get_settings()
    data = json.dumps(payload, sort_keys=True)
    sig = hmac.new(
        settings.session_secret.encode(), data.encode(), hashlib.sha256
    ).hexdigest()
    return f"{data}|{sig}"


def _verify_token(token: str) -> dict | None:
    """Verify and decode a session token. Returns payload or None."""
    settings = get_settings()
    if "|" not in token:
        return None
    data, sig = token.rsplit("|", 1)
    expected = hmac.new(
        settings.session_secret.encode(), data.encode(), hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(sig, expected):
        return None
    try:
        payload = json.loads(data)
    except json.JSONDecodeError:
        return None
    if payload.get("exp", 0) < time.time():
        return None
    return payload


@router.post("/auth/login", response_model=APIResponse)
async def login(body: LoginRequest, response: Response):
    user = _get_users().get(body.username)
    if not user or user["password"] != body.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    payload = {
        "sub": body.username,
        "role": user["role"],
        "name": user["name"],
        "exp": int(time.time()) + SESSION_MAX_AGE,
    }
    token = _sign_token(payload)

    response.set_cookie(
        key="medlit_session",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=SESSION_MAX_AGE,
        path="/",
    )
    return APIResponse(
        success=True,
        data={"username": body.username, "role": user["role"], "name": user["name"]},
    )


@router.post("/auth/demo", response_model=APIResponse)
async def demo_login(response: Response):
    """One-click viewer session so booth visitors never type credentials."""
    settings = get_settings()
    if not settings.demo_login_enabled:
        raise HTTPException(status_code=404, detail="Not found")

    user = _get_users()["demo"]
    payload = {
        "sub": "demo",
        "role": user["role"],
        "name": user["name"],
        "exp": int(time.time()) + SESSION_MAX_AGE,
    }
    token = _sign_token(payload)

    response.set_cookie(
        key="medlit_session",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=SESSION_MAX_AGE,
        path="/",
    )
    return APIResponse(
        success=True,
        data={"username": "demo", "role": user["role"], "name": user["name"]},
    )


@router.post("/auth/logout", response_model=APIResponse)
async def logout(response: Response):
    response.delete_cookie("medlit_session", path="/")
    return APIResponse(success=True, data=None)


@router.get("/auth/me", response_model=APIResponse)
async def me(medlit_session: str | None = Cookie(None)):
    settings = get_settings()
    if settings.auth_disabled:
        return APIResponse(
            success=True,
            data={"username": "dev", "role": "admin", "name": "Dev Mode"},
        )

    if not medlit_session:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = _verify_token(medlit_session)
    if payload is None:
        raise HTTPException(status_code=401, detail="Session expired")

    return APIResponse(
        success=True,
        data={
            "username": payload["sub"],
            "role": payload["role"],
            "name": payload["name"],
        },
    )
