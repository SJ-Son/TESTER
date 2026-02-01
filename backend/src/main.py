import logging
import os
import time

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from jose import jwt
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from backend.src.api.routers import api_router
from backend.src.api.v1.deps import limiter
from backend.src.auth import ALGORITHM
from backend.src.config.settings import settings

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="QA Test Code Generator API")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip Compression
app.add_middleware(GZipMiddleware, minimum_size=500)

# Rate Limiting Setup
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Middleware: Attach User to State (for Rate Limiting)
@app.middleware("http")
async def attach_user_to_state(request: Request, call_next):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
            request.state.user = {"id": payload.get("sub"), "email": payload.get("email")}
        except Exception:
            request.state.user = None
    else:
        request.state.user = None
    response = await call_next(request)
    return response


# Middleware: Security Headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    # HSTS
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

    # X-Content-Type-Options
    response.headers["X-Content-Type-Options"] = "nosniff"

    # X-Frame-Options
    response.headers["X-Frame-Options"] = "SAMEORIGIN"

    # Referrer-Policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Content-Security-Policy
    csp_policy = (
        "default-src 'self' https://accounts.google.com https://www.gstatic.com https://www.google.com; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://accounts.google.com https://www.google.com https://www.gstatic.com https://apis.google.com; "
        "style-src 'self' 'unsafe-inline' https://accounts.google.com https://fonts.googleapis.com https://www.gstatic.com; "
        "img-src 'self' data: https://*.googleusercontent.com https://www.gstatic.com https://www.google.com; "
        "font-src 'self' https://fonts.gstatic.com data:; "
        "connect-src 'self' https://accounts.google.com https://www.google.com; "
        "frame-src 'self' https://accounts.google.com https://www.google.com https://recaptcha.google.com;"
    )
    response.headers["Content-Security-Policy"] = csp_policy

    return response


# Middleware: Logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin-allow-popups"
        process_time = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s"
        )
        return response
    except Exception as e:
        logger.error(f"Request Failed: {e}")
        return StreamingResponse(
            iter([f"error: {str(e)}"]), media_type="text/plain", status_code=500
        )


# Include API Routers
app.include_router(api_router, prefix="/api")

# --- Static File Serving (Production) ---

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIST = "/app/frontend/dist"

if os.path.exists(FRONTEND_DIST):
    logger.info(f"✅ Found frontend at {FRONTEND_DIST}")
    # Mount assets
    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    # Serve robots.txt
    @app.get("/robots.txt")
    async def get_robots_txt():
        robots_file = os.path.join(FRONTEND_DIST, "robots.txt")
        if os.path.exists(robots_file):
            return FileResponse(robots_file)
        return {"error": "robots.txt not found"}

    # Serve sitemap.xml
    @app.get("/sitemap.xml")
    async def get_sitemap_xml():
        sitemap_file = os.path.join(FRONTEND_DIST, "sitemap.xml")
        if os.path.exists(sitemap_file):
            return FileResponse(sitemap_file)
        return {"error": "sitemap.xml not found"}

    # SPA Catch-all
    @app.get("/{rest_of_path:path}")
    async def serve_frontend(rest_of_path: str):
        if rest_of_path.startswith("api/"):
            raise HTTPException(status_code=404)

        index_file = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"error": "index.html not found in dist"}
else:
    logger.warning(f"❌ Frontend dist not found at {FRONTEND_DIST}. Serving API only.")

    @app.get("/")
    async def root():
        return {"message": "Gemini API Server is running. Frontend dist not found."}


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    logger.info(f"🚀 Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
