"""Console OIDC redirect auth — mock code flow for dev + real IdP config (CM-055)."""

from __future__ import annotations

import os
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import jwt
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="/console/auth", tags=["console-auth"])

_SESSION_COOKIE = "context_skills_session"
_PENDING: dict[str, str] = {}


def _secret() -> str:
    return os.environ.get("CONTEXT_SKILLS_OIDC_HMAC_SECRET", "dev-secret-at-least-32-characters-long")


def _issuer() -> str:
    return os.environ.get("CONTEXT_SKILLS_OIDC_ISSUER", "https://mock-idp.local")


def _audience() -> str:
    return os.environ.get("CONTEXT_SKILLS_OIDC_AUDIENCE", "context-skills-api")


def _issue_token(*, subject: str = "console-user", roles: str = "admin", tenant_id: str = "tenant-a") -> str:
    return jwt.encode(
        {
            "sub": subject,
            "iss": _issuer(),
            "aud": _audience(),
            "roles": roles,
            "tenant_id": tenant_id,
            "exp": datetime.now(timezone.utc) + timedelta(hours=8),
        },
        _secret(),
        algorithm="HS256",
    )


@router.get("/login")
def console_login(request: Request) -> RedirectResponse:
    state = secrets.token_urlsafe(16)
    _PENDING[state] = "pending"
    redirect_uri = str(request.url_for("console_callback"))
    params = {
        "state": state,
        "redirect_uri": redirect_uri,
        "client_id": "context-skills-console",
        "response_type": "code",
    }
    issuer = os.environ.get("CONTEXT_SKILLS_OIDC_AUTHORIZE_URL")
    if issuer:
        return RedirectResponse(f"{issuer}?{urlencode(params)}")
    return RedirectResponse(f"/console/auth/callback?{urlencode({'code': 'mock', 'state': state})}")


@router.get("/callback", name="console_callback")
def console_callback(code: str, state: str) -> RedirectResponse:
    if state not in _PENDING:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")
    del _PENDING[state]
    if code != "mock" and not os.environ.get("CONTEXT_SKILLS_OIDC_AUTHORIZE_URL"):
        raise HTTPException(status_code=400, detail="Unsupported auth code exchange in mock mode")
    token = _issue_token()
    redirect = RedirectResponse("/console/", status_code=302)
    redirect.set_cookie(
        _SESSION_COOKIE,
        token,
        httponly=True,
        samesite="lax",
        max_age=8 * 3600,
    )
    return redirect


@router.post("/logout")
def console_logout() -> RedirectResponse:
    redirect = RedirectResponse("/console/", status_code=302)
    redirect.delete_cookie(_SESSION_COOKIE)
    return redirect


@router.get("/session")
def console_session(request: Request) -> dict[str, str]:
    token = request.cookies.get(_SESSION_COOKIE, "")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"token": token}
