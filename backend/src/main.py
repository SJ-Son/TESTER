import logging
import os
import time
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from jose import jwt
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from src.api.routers import api_router
from src.api.v1.deps import limiter
from src.auth import ALGORITHM
from src.config.constants import NetworkConstants
from src.config.settings import settings
from src.exceptions import TurnstileError, ValidationError

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and Shutdown events.
    """
    # === Startup ===
    logger.info("🚀 Starting TESTER API...")

    logger.info("✅ gemini API configured.")

    # Validate Config
    if not settings.GEMINI_API_KEY:
        logger.critical("🔴 CRITICAL: GEMINI_API_KEY is missing!")
        # Application will fail at GeminiService __init__ level

    # Supabase 연결 검증
    try:
        from src.services.supabase_service import SupabaseService

        SupabaseService()  # Singleton 초기화
        logger.info("✅ Supabase 연결 검증 완료")
    except Exception as e:
        logger.error(f"❌ Supabase 연결 실패: {e}")
        logger.warning("⚠️ 일부 기능이 제한될 수 있습니다")

    # Redis Check
    try:
        from src.services.cache_service import CacheService

        cache_service = CacheService()
        cache_service.redis_client.ping()
        logger.info("✅ Redis connected.")
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        logger.warning(
            "⚠️  Caching will be unavailable. Application may run with degraded performance."
        )

    # Encryption Check
    try:
        from src.utils.security import EncryptionService

        EncryptionService()
        logger.info("✅ Encryption service ready.")
    except Exception as e:
        logger.critical(f"🔴 CRITICAL: Encryption setup failed: {e}")

    logger.info("🎉 TESTER API is ready!")

    yield

    # === Shutdown ===
    logger.info("🛑 Shutting down TESTER API...")

    # Redis cleanup
    try:
        from src.services.cache_service import RedisConnectionManager

        RedisConnectionManager.get_instance().close()
        logger.info("✅ Redis connections closed")
    except Exception as e:
        logger.warning(f"⚠️  Redis cleanup warning: {e}")

    logger.info("👋 Goodbye!")


app = FastAPI(title="QA Test Code Generator API", lifespan=lifespan)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip Compression
app.add_middleware(GZipMiddleware, minimum_size=NetworkConstants.GZIP_MIN_SIZE_BYTES)

# Rate Limiting Setup
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(TurnstileError)
async def turnstile_exception_handler(request: Request, exc: TurnstileError):
    return JSONResponse(
        status_code=400,
        content={"type": "error", "code": exc.code, "message": exc.message},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to catch unhandled errors."""
    # Log the full error for internal debugging
    logger.error(f"Global Exception: {exc}", exc_info=True)

    # Return a generic error message to the client to prevent information leakage
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal Server Error",
            "detail": "An internal server error occurred. Please contact support.",
        },
    )


# Prometheus Metrics
Instrumentator().instrument(app).expose(app)


# Middleware: Attach User to State (for Rate Limiting)
@app.middleware("http")
async def attach_user_to_state(request: Request, call_next):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            # SECURITY FIX: Prevent usage of empty secret which allows token forgery
            if not settings.SUPABASE_JWT_SECRET:
                logger.warning(
                    "SUPABASE_JWT_SECRET not set. Ignoring Authorization header to prevent security risk."
                )
                request.state.user = None
            else:
                payload = jwt.decode(token, settings.SUPABASE_JWT_SECRET, algorithms=[ALGORITHM])
                request.state.user = {"id": payload.get("sub"), "email": payload.get("email")}
        except Exception:
            request.state.user = None
    else:
        request.state.user = None
    response = await call_next(request)
    return response


# Middleware: Security Headers & Logging
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)

        # Security Headers
        response.headers[
            "Strict-Transport-Security"
        ] = "max-age=31536000; includeSubDomains; preload"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin-allow-popups"
        response.headers["Cross-Origin-Resource-Policy"] = "cross-origin"

        # Content-Security-Policy (Flattened to avoid parsing warnings)
        csp_policy = (
            "default-src 'self' https://accounts.google.com https://www.gstatic.com https://www.google.com https://challenges.cloudflare.com; "
            "script-src 'self' 'unsafe-inline' https://accounts.google.com https://www.google.com https://www.gstatic.com https://apis.google.com https://challenges.cloudflare.com https://www.googletagmanager.com; "
            "style-src 'self' 'unsafe-inline' https://accounts.google.com https://fonts.googleapis.com https://www.gstatic.com; "
            "img-src 'self' data: https://*.googleusercontent.com https://www.gstatic.com https://www.google.com https://www.googletagmanager.com https://www.google-analytics.com; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "connect-src 'self' https://*.supabase.co https://accounts.google.com https://www.google.com https://challenges.cloudflare.com https://www.google-analytics.com https://analytics.google.com https://www.googletagmanager.com; "
            "frame-src 'self' https://accounts.google.com https://challenges.cloudflare.com; "
            "frame-ancestors 'self' https://accounts.google.com;"
        )
        response.headers["Content-Security-Policy"] = csp_policy

        # Logging
        process_time = time.time() - start_time
        logger.info(
            f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s"
        )
        return response
    except ValidationError as e:
        logger.warning(f"Validation failed: {e.message}")
        # Return 200 OK with error payload to keep the browser console clean (no red lines for expected validation)
        return {
            "type": "error",
            "status": "validation_error",
            "detail": {"code": e.code, "message": e.message},
        }


# Health Check Endpoint (for monitoring and load balancers)
@app.get("/health")
async def health_check():
    """
    상세 인프라 헬스 체크 엔드포인트.

    Redis, Supabase, Gemini API 설정 상태를 확인하고
    각 서비스별 지연시간을 측정하여 반환합니다.
    """
    from datetime import datetime

    health_status = {
        "status": "healthy",  # healthy, degraded, unhealthy
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.7.0",
        "services": {},
    }

    overall_healthy = True

    # === Redis Check ===
    try:
        from src.services.cache_service import CacheService

        cache = CacheService()
        start_time = time.time()
        cache.redis_client.ping()
        latency_ms = (time.time() - start_time) * 1000

        pool_info = cache.redis_client.connection_pool
        health_status["services"]["redis"] = {
            "status": "up",
            "latency_ms": round(latency_ms, 2),
            "connection_pool": {
                "max_connections": pool_info.max_connections,
                "available": pool_info.max_connections - len(pool_info._available_connections),
            },
        }
    except Exception as e:
        overall_healthy = False
        health_status["services"]["redis"] = {
            "status": "down",
            "error": str(e)[:100],  # 에러 메시지 길이 제한
        }

    # === Supabase Check ===
    try:
        from src.services.supabase_service import SupabaseService

        supabase = SupabaseService()
        start_time = time.time()
        # Simple table existence check
        supabase.client.table("generation_history").select("id").limit(1).execute()
        latency_ms = (time.time() - start_time) * 1000

        health_status["services"]["supabase"] = {
            "status": "up",
            "latency_ms": round(latency_ms, 2),
            "table_accessible": True,
        }
    except Exception as e:
        overall_healthy = False
        health_status["services"]["supabase"] = {"status": "down", "error": str(e)[:100]}

    # === Gemini API Check ===
    gemini_configured = bool(settings.GEMINI_API_KEY)
    health_status["services"]["gemini"] = {
        "status": "configured" if gemini_configured else "not_configured",
        "model": settings.DEFAULT_GEMINI_MODEL,
    }

    if not gemini_configured:
        overall_healthy = False

    # === Overall Status ===
    if not overall_healthy:
        health_status["status"] = "degraded"

    return health_status


# API Routes
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
