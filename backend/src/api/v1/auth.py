import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request, Response
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
async def login(request: Request, provider: str = "google", next: str = "/"):
    """
    Initiate OAuth login from Backend.
    """
    supabase = get_supabase_client()

    # Dynamic Callback URL Construction
    # This ensures it works for Localhost, Staging, and Production automatically.
    # We use the request's base URL which mirrors how the client accessed the API.

    # request.url.scheme: http or https
    # request.url.netloc: host:port
    base_url = str(request.base_url).rstrip("/")

    # Force HTTPS in non-local environments if missing (Cloud Run usually handles this, but good to be safe)
    if (
        "localhost" not in base_url
        and "127.0.0.1" not in base_url
        and base_url.startswith("http://")
    ):
        base_url = base_url.replace("http://", "https://")

    callback_url = f"{base_url}/api/auth/callback"
    logger.info(f"Initiating Login. Base URL: {base_url}, Generated Callback URL: {callback_url}")

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
        # Heuristic: First origin
        if settings.ENV.lower() in ["production", "staging"]:
            # Use request 'Referer' or configured Frontend URL?
            # For now, let's assume relative redirect "/" if served from same origin (which is the case in Prod/Staging)
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
