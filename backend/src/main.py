from fastapi import FastAPI, Request, Query, HTTPException, Depends
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from backend.src.services.gemini_service import GeminiService
from backend.src.languages.factory import LanguageFactory
from backend.src.config.settings import settings
import asyncio
import os
from datetime import timedelta

import logging
import time
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.security import APIKeyHeader
from backend.src.auth import (
    create_access_token, 
    verify_google_token, 
    get_current_user, 
    verify_recaptcha,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from pydantic import BaseModel
from jose import jwt
from backend.src.auth import ALGORITHM

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="QA Test Code Generator API")

# Step 3: CORS Setup - Tightened security
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=500)

# Step 4: Rate Limiting Setup
def get_user_identifier(request: Request):
    # 인증된 사용이면 user id, 아니면 IP 기반
    user = getattr(request.state, "user", None)
    if user:
        return f"user_{user['id']}"
    return get_remote_address(request)

limiter = Limiter(key_func=get_user_identifier)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.middleware("http")
async def attach_user_to_state(request: Request, call_next):
    # Authorization 헤더가 있으면 user 정보를 state에 저장 (Rate Limit에서 사용)
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
            request.state.user = {"id": payload.get("sub"), "email": payload.get("email")}
        except:
            request.state.user = None
    else:
        request.state.user = None
    response = await call_next(request)
    return response

# Step 5: Security - Internal API Key
API_KEY_NAME = "X-TESTER-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(api_key: str = Depends(api_key_header)):
    if not api_key or api_key != settings.TESTER_INTERNAL_SECRET:
        logger.warning(f"Unauthorized access attempt with key: {api_key}")
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Invalid Internal API Key"
        )
    return api_key

# Step 6: Auth Endpoints
class TokenRequest(BaseModel):
    id_token: str

@app.post("/api/auth/google")
async def google_auth(data: TokenRequest):
    user_info = verify_google_token(data.id_token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid Google Token")
    
    access_token = create_access_token(
        data={"sub": user_info["sub"], "email": user_info["email"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Step 5: Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        # Google OAuth/GSI requires allow-popups if COOP is active
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin-allow-popups"
        process_time = time.time() - start_time
        logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
        return response
    except Exception as e:
        logger.error(f"Request Failed: {e}")
        return StreamingResponse(iter([f"error: {str(e)}"]), media_type="text/plain", status_code=500)

# Initialize Service
try:
    if not os.getenv("GEMINI_API_KEY"):
        logger.warning("GEMINI_API_KEY not found in env. Service might fail.")
    gemini_service = GeminiService(model_name="gemini-3-flash-preview")
except Exception as e:
    logger.error(f"Failed to initialize GeminiService: {e}")
    gemini_service = None

# --- API Endpoints ---


class GenerateRequest(BaseModel):
    input_code: str
    language: str
    model: str = "gemini-3-flash-preview"
    recaptcha_token: str = Field(..., description="reCAPTCHA v3 token")

@app.post("/api/generate")
@limiter.limit("5/minute")
async def generate_test(
    request: Request, 
    data: GenerateRequest,
    current_user: dict = Depends(get_current_user)
):
    # 1. reCAPTCHA Verify
    if not await verify_recaptcha(data.recaptcha_token):
        raise HTTPException(status_code=403, detail="reCAPTCHA verification failed (Bot detected)")

    # 2. Logic starts...
    """Streams generated code as raw text (SSE)."""
    # 1. Validation
    strategy = LanguageFactory.get_strategy(data.language)
    valid, msg = strategy.validate_code(data.input_code)
    
    if not valid:
        return StreamingResponse(iter([f"ERROR: {msg}"]), media_type="text/plain")

    # 2. Setup System Instruction
    system_instruction = strategy.get_system_instruction()
    gemini_service.model_name = data.model

    async def generate_stream():
        try:
            # gemini_service.generate_test_code is now an async generator
            async for chunk in gemini_service.generate_test_code(
                data.input_code, 
                system_instruction=system_instruction, 
                stream=True
            ):
                if chunk:
                    yield chunk
                    # No need for manual sleep if it's truly async streaming, 
                    # but keeping it minimal if required for flow control.
                    await asyncio.sleep(0.01)
            
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"\nERROR: {str(e)}"

    return StreamingResponse(generate_stream(), media_type="text/event-stream")

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "gemini-api"}

# --- Static File Serving (Production) ---

# We use absolute paths based on /app in container
# Structure: /app/backend/src/main.py
#           /app/frontend/dist/index.html
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
FRONTEND_DIST = "/app/frontend/dist"

if os.path.exists(FRONTEND_DIST):
    logger.info(f"✅ Found frontend at {FRONTEND_DIST}")
    # Mount assets (common in Vite build)
    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    # Serve index.html for SPA
    @app.get("/{rest_of_path:path}")
    async def serve_frontend(rest_of_path: str):
        # Don't intercept /api routes
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

