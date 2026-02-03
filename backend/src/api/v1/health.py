from fastapi import APIRouter, Depends

from backend.src.api.v1.deps import get_supabase_service
from backend.src.services.supabase_service import SupabaseService

router = APIRouter()


@router.get("/health")
async def health_check(
    supabase: SupabaseService = Depends(get_supabase_service),
):
    db_status = "connected" if supabase.is_connected() else "disconnected"
    return {"status": "ok", "service": "gemini-api", "database": db_status}
