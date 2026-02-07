import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel
from src.repositories.base_repository import BaseRepository
from src.services.supabase_service import SupabaseService
from src.utils.security import EncryptionService


class GenerationModel(BaseModel):
    id: Optional[UUID] = None
    user_id: Optional[str] = None  # Changed to str
    input_code: str
    generated_code: str
    language: str
    model: str
    created_at: Optional[datetime] = None


class GenerationRepository(BaseRepository[GenerationModel]):
    """생성 이력 저장소"""

    def __init__(self, supabase_service: SupabaseService):
        super().__init__(supabase_service, "generation_history", GenerationModel)
        self.encryption = EncryptionService()
        self.logger = logging.getLogger(__name__)

    def create_history(
        self,
        user_id: str,  # Changed to str
        input_code: str,
        generated_code: str,
        language: str,
        model: str,
    ) -> Optional[GenerationModel]:
        """이력 생성 (암호화 저장)"""

        # 민감 데이터 암호화
        encrypted_input = self.encryption.encrypt(input_code)
        encrypted_output = self.encryption.encrypt(generated_code)

        entry = GenerationModel(
            user_id=user_id,
            input_code=encrypted_input,
            generated_code=encrypted_output,
            language=language,
            model=model,
        )
        # exclude_none=True to let DB handle defaults like id, created_at
        data = entry.model_dump(exclude={"id", "created_at"}, exclude_none=True)

        response = self.client.table(self.table_name).insert(data).execute()
        if response.data:
            created_model = self.model_cls(**response.data[0])
            # Return decrypted data for immediate usage if needed
            created_model.input_code = input_code
            created_model.generated_code = generated_code
            return created_model
        return None

    def get_user_history(self, user_id: str, limit: int = 50) -> list[GenerationModel]:
        """사용자 이력 조회 (복호화 반환)"""
        # DB 쿼리 실패시 예외가 전파되도록 둠 (API layer에서 500 처리)
        response = (
            self.client.table(self.table_name)
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        results = []
        for item in response.data:
            model = self.model_cls(**item)
            try:
                # 복호화 시도
                model.input_code = self.encryption.decrypt(model.input_code)
                model.generated_code = self.encryption.decrypt(model.generated_code)
                results.append(model)
            except Exception:
                # 복호화 실패 시 로그 남기고 해당 항목은 결과에서 제외
                self.logger.error(f"Failed to decrypt history item {model.id}", exc_info=True)
                # corrupted item skipped
        return results