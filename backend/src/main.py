from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from backend.src.services.gemini_service import GeminiService
from backend.src.languages.factory import LanguageFactory
import json
import asyncio
import os

import logging
import time
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.security import APIKeyHeader

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="QA Test Code Generator API")

# Step 3: CORS Setup - Allow frontend development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, you might want to restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Step 4: Rate Limiting Setup
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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

# Step 5: Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
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

from pydantic import BaseModel

class GenerateRequest(BaseModel):
    input_code: str = Field(..., max_length=10000, description="테스트할 소스 코드 (최대 10,000자)")
    language: str
    model: str
    use_reflection: bool = False

@app.post("/api/generate")
@limiter.limit("5/minute")
async def generate_code(req: GenerateRequest, request: Request, _auth=Depends(verify_api_key)):
    """Streams generated code as raw text (SSE)."""
    # 1. Validation
    strategy = LanguageFactory.get_strategy(req.language)
    valid, msg = strategy.validate_code(req.input_code)
    
    if not valid:
        return StreamingResponse(iter([f"ERROR: {msg}"]), media_type="text/plain")

    # 2. Setup System Instruction
    system_instruction = strategy.get_system_instruction()
    gemini_service.model_name = req.model

    async def generate_stream():
        try:
            generator = gemini_service.generate_test_code(
                req.input_code, 
                system_instruction=system_instruction, 
                stream=True,
                use_reflection=req.use_reflection
            )
            
            # Simple metadata headers if needed (optional)
            # yield "data: [START]\n\n"

            for chunk in generator:
                if chunk:
                    # Pure text streaming for Vue to consume
                    yield chunk
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

