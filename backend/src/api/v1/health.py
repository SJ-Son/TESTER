from fastapi import APIRouter, Depends
from src.api.v1.deps import get_supabase_service
from src.services.supabase_service import SupabaseService

router = APIRouter()


@router.get("/health")
async def health_check(
    supabase: SupabaseService = Depends(get_supabase_service),
):
    db_info = supabase.get_connection_status()
    return {
        "status": "ok",
        "service": "gemini-api",
        "database": {
            "status": "connected" if db_info["connected"] else "disconnected",
            "reason": db_info["reason"],
        },
    }
