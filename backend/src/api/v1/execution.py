from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api.v1.deps import limiter
from src.auth import get_current_user
from src.services.execution_service import ExecutionService

router = APIRouter()
execution_service = ExecutionService()


class ExecuteRequest(BaseModel):
    input_code: str
    test_code: str
    language: str


@router.post("/execute")
@limiter.limit("5/minute")
async def execute_code(
    request: Request,
    data: ExecuteRequest,
    current_user: dict = Depends(get_current_user),
):
    """Execute code in a sandboxed environment."""
    result = execution_service.execute_code(data.input_code, data.test_code, data.language)
    return result
