import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import RedirectResponse
from src.config.settings import settings
from supabase import Client, create_client

router = APIRouter()
logger = logging.getLogger(__name__)


# Initialize Supabase Client (Admin/Service Role not strictly needed for auth exchange,
# but we need a client to talk to Auth API. Standard client is fine.)
# However, for exchange_code_for_session, we usually use the client.
def get_supabase_client() -> Client:
    url = settings.SUPABASE_URL
    key = settings.SUPABASE_ANON_KEY
    return create_client(url, key)


@router.get("/login")
async def login(provider: str = "google", next: str = "/"):
    """
    Initiate OAuth login from Backend.
    Redirects to Supabase Auth URL with backend callback.
    """
    supabase = get_supabase_client()

    # Construct the callback URL
    # In Prod: https://my-app.com/api/auth/callback
    # In Dev: http://localhost:8000/api/auth/callback

    # We can detect host from request, or use configured settings.
    # ideally settings.API_BASE_URL + "/api/auth/callback"

    # For now, let's use a heuristic or env var
    # If we are in dev (localhost), we assume localhost:8000
    if settings.is_production:
        # Need a way to know the production backend URL.
        # Assuming it's the same domain as frontend for now?
        # Or configured in SUPABASE_URL configuration on dashboard?
        # Actually, Supabase needs the `redirectTo` to be whitelisted.
        # Let's use the referer-based approach or hardcode for now if env not set.
        callback_url = f"{settings.ALLOWED_ORIGINS.split(',')[0]}/api/auth/callback"
    else:
        callback_url = "http://localhost:8000/api/auth/callback"

    # Get OAuth URL
    res = supabase.auth.sign_in_with_oauth(
        {
            "provider": provider,
            "options": {
                "redirect_to": callback_url,
                # "scopes": "..." # if needed
            },
        }
    )

    if res.url:
        return RedirectResponse(url=res.url)

    raise HTTPException(status_code=500, detail="Failed to generate auth URL")


@router.get("/callback")
async def auth_callback(
    code: str, response: Response, next_url: Optional[str] = Query(default="/", alias="next")
):
    """
    Exchange auth code for session and set HttpOnly cookies.
    """
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code missing")

    try:
        supabase = get_supabase_client()

        # Exchange code for session
        res = supabase.auth.exchange_code_for_session({"auth_code": code})

        session = res.session
        if not session:
            raise HTTPException(status_code=401, detail="Failed to create session")

        # Set Cookies
        # Access Token
        response.set_cookie(
            key="access_token",
            value=session.access_token,
            httponly=True,
            secure=settings.is_production,  # True in Prod, False in Dev if over HTTP
            samesite="lax",  # Strict might be too aggressive for redirects
            max_age=session.expires_in,
        )

        # Refresh Token (Optional, but good for staying logged in)
        if session.refresh_token:
            response.set_cookie(
                key="refresh_token",
                value=session.refresh_token,
                httponly=True,
                secure=settings.is_production,
                samesite="lax",
                max_age=60 * 60 * 24 * 30,  # 30 days usually
            )

        # Redirect to Frontend
        # In Docker/Prod, we might need a specific URL.
        # But since valid redirection, a relative path usually works if on same domain.
        # If frontend is on user's browser, we just redirect there.
        # For local dev `localhost:5173` vs `localhost:8000`, we need absolute URL.

        # Heuristic: First origin
        if settings.is_production:
            # Use request 'Referer' or configured Frontend URL?
            # For now, let's assume relative redirect "/" if served from same origin (which is the case in Prod)
            target_url = next_url
        else:
            # Dev environment: Redirect to Vite port
            target_url = f"http://localhost:5173{next_url}"

        logger.info(f"Auth successful. Redirecting to {target_url}")
        return RedirectResponse(url=target_url)

    except Exception as e:
        logger.error(f"Auth Callback Error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/logout")
async def logout(response: Response):
    """
    Clear auth cookies.
    """
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {"message": "Logged out successfully"}
