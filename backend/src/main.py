import logging
import os
import time
import uuid
from contextlib import asynccontextmanager

import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import jwt
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from src.api.routers import api_router
from src.api.v1.deps import limiter
from src.auth import ALGORITHM
from src.config.constants import NetworkConstants
from src.config.settings import settings
from src.exceptions import TurnstileError, ValidationError
from src.utils.logger import get_logger, setup_logging, trace_id_ctx

# 로깅 설정 초기화
setup_logging(log_level=logging.INFO)
logger = get_logger(__name__)

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기를 관리합니다 (시작/종료).

    Yields:
        None
    """
    # === 시작 (Startup) ===
    logger.info("TESTER API 서버를 시작합니다")

    # 설정 검증
    if not settings.GEMINI_API_KEY.get_secret_value():
        logger.critical("GEMINI_API_KEY가 설정되지 않았습니다")
    else:
        # Gemini API 설정
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY.get_secret_value())
            logger.info("Gemini API 설정이 완료되었습니다")
        except Exception as e:
            logger.critical(f"Gemini API 설정에 실패했습니다: {e}")

    # Supabase 연결 검증
    try:
        from src.services.supabase_service import SupabaseService

        SupabaseService()  # 싱글톤 초기화
        logger.info("Supabase 연결이 확인되었습니다")
    except Exception as e:
        logger.error(f"Supabase 연결에 실패했습니다: {e}")
        logger.warning("일부 기능이 정상적으로 작동하지 않을 수 있습니다")

    # Redis 연결 확인
    try:
        from src.services.cache_service import CacheService

        cache_service = CacheService()
        await cache_service.ping()
        logger.info("Redis 연결에 성공했습니다")
    except Exception as e:
        logger.error(f"Redis 연결에 실패했습니다: {e}")
        logger.warning("캐싱 기능을 사용할 수 없으며 성능 저하가 발생할 수 있습니다")

    # 암호화 키 확인
    try:
        from src.utils.security import EncryptionService

        EncryptionService()
        logger.info("암호화 서비스가 준비되었습니다")
    except Exception as e:
        logger.critical(f"암호화 설정에 실패했습니다: {e}")

    logger.info("TESTER API 서버가 요청을 처리할 준비가 되었습니다")

    yield

    # === 종료 (Shutdown) ===
    logger.info("TESTER API 서버를 종료합니다")

    # Redis 연결 정리
    try:
        from src.services.cache_service import RedisConnectionManager

        await RedisConnectionManager.get_instance().close()
        logger.info("Redis 연결이 종료되었습니다")
    except Exception as e:
        logger.warning(f"Redis 정리 중 오류가 발생했습니다: {e}")

    # ExecutionService 정리
    try:
        from src.services.execution_service import ExecutionService

        await ExecutionService().close()
        logger.info("ExecutionService 연결이 종료되었습니다")
    except Exception as e:
        logger.warning(f"ExecutionService 정리 중 오류가 발생했습니다: {e}")

    logger.info("서버가 안전하게 종료되었습니다")


app = FastAPI(title="QA Test Code Generator API", lifespan=lifespan)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip 압축 설정
app.add_middleware(GZipMiddleware, minimum_size=NetworkConstants.GZIP_MIN_SIZE_BYTES)

# Rate Limiting 설정
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# 미들웨어: Trace ID 생성 및 주입
@app.middleware("http")
async def trace_id_middleware(request: Request, call_next):
    """요청마다 고유한 Trace ID를 생성하고 컨텍스트에 설정합니다."""
    trace_id = str(uuid.uuid4())
    trace_id_ctx.set(trace_id)
    response = await call_next(request)
    response.headers["X-Trace-ID"] = trace_id
    return response


@app.exception_handler(TurnstileError)
async def turnstile_exception_handler(request: Request, exc: TurnstileError):
    return JSONResponse(
        status_code=400,
        content={"type": "error", "code": exc.code, "message": exc.message},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """전역 예외 처리기 (처리되지 않은 오류 포착).

    Args:
        request: HTTP 요청 객체.
        exc: 발생한 예외 객체.
    """

    # HTTP 예외는 그대로 통과
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    # 디버깅을 위해 전체 에러 로깅
    logger.error(f"처리되지 않은 예외 발생: {exc}", exc_info=True)

    # 클라이언트에게는 정보 유출 방지를 위해 일반적인 에러 메시지 반환
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal Server Error",
            "code": "INTERNAL_ERROR",
        },
    )


# 미들웨어: Content-Length 제한 (Slowloris / 대용량 페이로드 방지)
@app.middleware("http")
async def limit_content_length(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length:
        limit = 10 * 1024 * 1024  # 10 MB 제한
        if int(content_length) > limit:
            return JSONResponse(
                status_code=413,
                content={"detail": "Request entity too large"},
            )
    response = await call_next(request)
    return response


# Prometheus 메트릭
Instrumentator().instrument(app).expose(app)


# 미들웨어: 사용자 상태 주입 (Rate Limiting용)
@app.middleware("http")
async def attach_user_to_state(request: Request, call_next):
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            # 보안 수정: 빈 시크릿 사용 방지
            if not settings.SUPABASE_JWT_SECRET.get_secret_value():
                logger.warning(
                    "SUPABASE_JWT_SECRET이 설정되지 않았습니다. 보안을 위해 인증 헤더를 무시합니다"
                )
                request.state.user = None
            else:
                # audience 검증을 비활성화하여 python-jose와 동일한 동작 보장
                payload = jwt.decode(
                    token,
                    settings.SUPABASE_JWT_SECRET.get_secret_value(),
                    algorithms=[ALGORITHM],
                    options={"verify_aud": False},
                )
                request.state.user = {"id": payload.get("sub"), "email": payload.get("email")}
        except jwt.PyJWTError:
            logger.warning("Invalid JWT token detected")
            request.state.user = None
        except Exception as e:
            logger.error(f"Unexpected error during JWT decoding: {e}")
            request.state.user = None
    else:
        request.state.user = None
    response = await call_next(request)
    return response


# 미들웨어: 보안 헤더 및 로깅
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)

        # 보안 헤더 설정
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains; preload"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin-allow-popups"
        response.headers["Cross-Origin-Resource-Policy"] = "cross-origin"

        # Content-Security-Policy (구문 분석 경고 방지를 위해 단일 문자열로 병합)
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

        # 로깅
        process_time = time.time() - start_time
        logger.info_ctx(
            "HTTP 요청 처리 완료",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration=f"{process_time:.4f}s",
        )
        return response
    except ValidationError as e:
        logger.warning(f"유효성 검사 실패: {e.message}")
        # 브라우저 콘솔 오류 방지를 위해 200 OK와 에러 페이로드 반환
        return {
            "type": "error",
            "status": "validation_error",
            "detail": {"code": e.code, "message": e.message},
        }


@app.get("/health")
async def health_check():
    """상세 인프라 상태를 확인하는 엔드포인트.

    Redis, Supabase, Gemini API 설정 상태를 확인하고
    각 서비스별 지연시간을 측정하여 반환합니다.

    Returns:
        서비스별 상태 정보가 담긴 JSON 객체.
    """
    from datetime import datetime

    health_status = {
        "status": "healthy",  # healthy, degraded, unhealthy
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.7.0",
        "services": {},
    }

    overall_healthy = True

    try:
        from src.services.cache_service import CacheService

        cache = CacheService()
        start_time = time.time()
        await cache.ping()
        latency_ms = (time.time() - start_time) * 1000

        pool_info = cache.redis_client.connection_pool
        health_status["services"]["redis"] = {
            "status": "up",
            "latency_ms": round(latency_ms, 2),
            "connection_pool": {
                "max_connections": pool_info.max_connections,
            },
        }
    except Exception as e:
        overall_healthy = False
        health_status["services"]["redis"] = {
            "status": "down",
            "error": str(e)[:100],  # 에러 메시지 길이 제한
        }

    try:
        from src.services.supabase_service import SupabaseService

        supabase = SupabaseService()
        start_time = time.time()
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

    gemini_configured = bool(settings.GEMINI_API_KEY.get_secret_value())
    health_status["services"]["gemini"] = {
        "status": "configured" if gemini_configured else "not_configured",
        "model": settings.DEFAULT_GEMINI_MODEL,
    }

    if not gemini_configured:
        overall_healthy = False

    if not overall_healthy:
        health_status["status"] = "degraded"

    return health_status


app.include_router(api_router, prefix="/api")


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIST = "/app/frontend/dist"

if os.path.exists(FRONTEND_DIST):
    logger.info(f"프론트엔드 빌드 파일을 발견했습니다: {FRONTEND_DIST}")
    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/robots.txt")
    async def get_robots_txt():
        robots_file = os.path.join(FRONTEND_DIST, "robots.txt")
        if os.path.exists(robots_file):
            return FileResponse(robots_file)
        return {"error": "robots.txt not found"}

    @app.get("/sitemap.xml")
    async def get_sitemap_xml():
        sitemap_file = os.path.join(FRONTEND_DIST, "sitemap.xml")
        if os.path.exists(sitemap_file):
            return FileResponse(sitemap_file)
        return {"error": "sitemap.xml not found"}

    @app.get("/{rest_of_path:path}")
    async def serve_frontend(rest_of_path: str):
        if rest_of_path.startswith("api/"):
            raise HTTPException(status_code=404)

        index_file = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"error": "index.html not found in dist"}
else:
    logger.warning(f"프론트엔드 배포 경로를 찾을 수 없습니다: {FRONTEND_DIST}. API만 서빙합니다")

    @app.get("/")
    async def root():
        return {"message": "Gemini API 서버가 동작 중입니다. 프론트엔드는 제공되지 않습니다."}
