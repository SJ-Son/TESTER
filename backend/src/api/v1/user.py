import logging

from fastapi import APIRouter, Depends, HTTPException
from src.auth import get_current_user
from src.services.supabase_service import SupabaseService
from src.types import AuthenticatedUser
from starlette.concurrency import run_in_threadpool

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/status")
async def get_user_status(
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Get user's current usage status and quota.
    """
    try:
        supabase = SupabaseService()
        current_usage = await run_in_threadpool(supabase.check_weekly_quota, current_user["id"])

        # Hardcoded limit for now, ideally strictly coupled with generator.py
        WEEKLY_LIMIT = 30

        return {
            "email": current_user["email"],
            "weekly_usage": current_usage,
            "weekly_limit": WEEKLY_LIMIT,
            "remaining": max(0, WEEKLY_LIMIT - current_usage),
        }
    except Exception as e:
        logger.error(f"Failed to get user status: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user status") from e
