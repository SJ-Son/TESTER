from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from backend.src.repositories.base_repository import BaseRepository
from backend.src.services.supabase_service import SupabaseService
from backend.src.utils.security import EncryptionService


class GenerationModel(BaseModel):
    id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    input_code: str
    language: str
    model: str
    created_at: Optional[datetime] = None


class GenerationRepository(BaseRepository[GenerationModel]):
    """생성 이력 저장소"""

    def __init__(self, supabase_service: SupabaseService):
        super().__init__(supabase_service, "generation_history", GenerationModel)
        self.encryption = EncryptionService()

    def create_history(
        self, user_id: Optional[UUID], input_code: str, language: str, model: str
    ) -> Optional[GenerationModel]:
        """이력 생성 (암호화 저장)"""

        # 민감 데이터 암호화
        encrypted_code = self.encryption.encrypt(input_code)

        entry = GenerationModel(
            user_id=user_id, input_code=encrypted_code, language=language, model=model
        )
        # exclude_none=True to let DB handle defaults like id, created_at
        data = entry.model_dump(exclude={"id", "created_at"}, exclude_none=True)

        try:
            response = self.client.table(self.table_name).insert(data).execute()
            if response.data:
                created_model = self.model_cls(**response.data[0])
                created_model.input_code = self.encryption.decrypt(created_model.input_code)
                return created_model
            return None
        except Exception:
            return None
