from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from backend.src.repositories.base_repository import BaseRepository
from backend.src.services.supabase_service import SupabaseService


class TestLogModel(BaseModel):
    id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    input_code: str
    language: str
    model: str
    created_at: Optional[datetime] = None


class TestLogRepository(BaseRepository[TestLogModel]):
    """Test Logs 저장소"""

    def __init__(self, supabase_service: SupabaseService):
        super().__init__(supabase_service, "test_logs", TestLogModel)

    def create_log(
        self, user_id: Optional[UUID], input_code: str, language: str, model: str
    ) -> Optional[TestLogModel]:
        """로그 생성"""
        log_entry = TestLogModel(
            user_id=user_id, input_code=input_code, language=language, model=model
        )
        # exclude_none=True to let DB handle defaults like id, created_at
        # But Supabase insert expects dict. BaseRepository.create uses model_dump.
        # We need to ensure we don't send None for ID if we want DB to generate it,
        # or handle it in BaseRepository.
        # For now, let's rely on BaseRepository's generic create.

        # However, BaseRepository uses data.model_dump().
        # If id is None, it might send "id": null, which is fine for UUID default?
        # Usually better to exclude it. Pydantic model_dump(exclude_unset=True) might be better if we didn't set it.
        # But here we set it to None.

        # Let's override create slightly or assume BaseRepository logic.
        # Actually, let's just implement a specific method here that handles the business logic of logging.

        data = log_entry.model_dump(exclude={"id", "created_at"}, exclude_none=True)

        try:
            response = self.client.table(self.table_name).insert(data).execute()
            if response.data:
                return self.model_cls(**response.data[0])
            return None
        except Exception:
            # Logger usage from base or import
            return None
