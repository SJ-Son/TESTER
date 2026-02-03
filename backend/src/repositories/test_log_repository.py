from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from backend.src.repositories.base_repository import BaseRepository
from backend.src.services.supabase_service import SupabaseService
from backend.src.utils.security import EncryptionService


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
        self.encryption = EncryptionService()

    def create_log(
        self, user_id: Optional[UUID], input_code: str, language: str, model: str
    ) -> Optional[TestLogModel]:
        """로그 생성 (암호화 저장)"""

        # 민감 데이터 암호화
        encrypted_code = self.encryption.encrypt(input_code)

        log_entry = TestLogModel(
            user_id=user_id, input_code=encrypted_code, language=language, model=model
        )
        # exclude_none=True to let DB handle defaults like id, created_at
        data = log_entry.model_dump(exclude={"id", "created_at"}, exclude_none=True)

        try:
            response = self.client.table(self.table_name).insert(data).execute()
            if response.data:
                # 반환 시에는 복호화해서 전달?
                # 보통 저장 후 확인용으로 반환할 땐 원본을 반환하거나, 복호화 수행.
                # 여기선 create_log의 리턴값을 UI에서 바로 쓰진 않지만, 일관성을 위해 복호화
                # (단, user_id 등 메타데이터만 쓰는 경우가 많음).
                # 일단은 메모리 상의 원본(input_code)이 있으므로 그것을 쓰는게 맞지만,
                # DB에서 막 가져온 데이터라 치고 복호화 로직을 넣는게 안전.

                created_model = self.model_cls(**response.data[0])
                created_model.input_code = self.encryption.decrypt(created_model.input_code)
                return created_model
            return None
        except Exception:
            # Logger usage from base or import
            return None
