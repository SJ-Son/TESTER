from datetime import datetime
from typing import Optional, Union
from uuid import UUID

import orjson
from pydantic import BaseModel
from src.repositories.base_repository import BaseRepository
from src.services.cache_service import CacheService
from src.services.supabase_service import SupabaseService
from src.utils.logger import get_logger
from src.utils.security import EncryptionService
from starlette.concurrency import run_in_threadpool

logger = get_logger(__name__)


class GenerationModel(BaseModel):
    id: Optional[UUID] = None
    user_id: Optional[str] = None  # Changed to str
    input_code: str
    generated_code: str
    language: str
    model: str
    created_at: Optional[datetime] = None


class GenerationRepository(BaseRepository[GenerationModel]):
    """생성 이력(History) 테이블을 관리하는 레포지토리.

    코드 생성 이력의 저장 및 조회를 담당하며, 데이터 암호화/복호화를 처리합니다.
    """

    def __init__(self, supabase_service: SupabaseService):
        """GenerationRepository 인스턴스를 초기화합니다."""
        super().__init__("generation_history")
        self.encryption = EncryptionService()
        self.cache_service = CacheService()

    def _create_history_sync(
        self,
        user_id: str,
        input_code: str,
        generated_code: str,
        language: str,
        model: str,
    ) -> Union[GenerationModel, None]:
        """생성 이력을 저장합니다 (동기)."""
        try:
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
            # exclude_none=True: DB 기본값(id, created_at) 사용을 위해 None 제외
            data = entry.model_dump(exclude={"id", "created_at"}, exclude_none=True)

            response = self.client.table(self.table_name).insert(data).execute()
            if response.data:
                # 반환 시에는 복호화된 상태로 반환하도록 객체 생성
                created_model = self.model_cls(**response.data[0])
                created_model.input_code = input_code  # 원본 사용
                created_model.generated_code = generated_code  # 원본 사용
                return created_model
            return None
        except Exception as e:
            logger.error(f"이력 저장 실패: {e}", exc_info=True)
            raise

    async def create_history(
        self,
        user_id: str,
        input_code: str,
        generated_code: str,
        language: str,
        model: str,
    ) -> Union[GenerationModel, None]:
        """생성 이력을 저장합니다 (비동기).

        입력 코드와 생성된 코드는 암호화되어 저장됩니다.
        저장 후 사용자의 이력 캐시를 무효화합니다.

        Args:
            user_id: 사용자 ID.
            input_code: 사용자 입력 코드.
            generated_code: 생성된 테스트 코드.
            language: 프로그래밍 언어.
            model: 사용된 모델명.

        Returns:
            저장된 GenerationModel 객체 (실패 시 None).
        """
        result = await run_in_threadpool(
            self._create_history_sync,
            user_id,
            input_code,
            generated_code,
            language,
            model,
        )

        # 캐시 무효화
        # 키 패턴: history:{user_id}:*
        try:
            await self.cache_service.clear(f"history:{user_id}:*")
        except Exception as e:
            logger.warning(f"Failed to clear cache for user {user_id}: {e}")

        return result

    def _get_user_history_sync(self, user_id: str, limit: int = 50) -> list[GenerationModel]:
        """사용자의 생성 이력을 조회합니다 (동기).

        최신순으로 정렬하여 조회하며, 저장된 코드는 복호화하여 반환합니다.
        """
        try:
            response = (
                self.client.table(self.table_name)
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )

            history_items = []
            for item in response.data:
                try:
                    # 데이터 복호화
                    decrypted_input = self.encryption.decrypt(item["input_code"])
                    decrypted_output = self.encryption.decrypt(item["generated_code"])

                    history_items.append(
                        GenerationModel(
                            id=item["id"],
                            user_id=item[
                                "user_id"
                            ],  # Added user_id to maintain consistency with GenerationModel
                            input_code=decrypted_input,
                            generated_code=decrypted_output,
                            language=item["language"],
                            model=item["model"],
                            created_at=item["created_at"],
                        )
                    )
                except Exception as e:
                    logger.warning(
                        f"이력 데이터 복호화 실패 (건너뜀) - history_id: {item.get('id')}, error: {str(e)}"
                    )
                    continue

            return history_items

        except Exception as e:
            logger.error(f"이력 조회 중 오류 발생: {e}")
            raise

    async def get_user_history(self, user_id: str, limit: int = 50) -> list[GenerationModel]:
        """사용자의 생성 이력을 조회합니다 (비동기, 캐싱 적용).

        Redis 캐시를 먼저 확인하고, 없으면 DB에서 조회 후 캐싱합니다.
        캐시 TTL은 1시간(3600초)입니다.

        Args:
            user_id: 사용자 ID.
            limit: 조회할 최대 개수 (기본값: 50).

        Returns:
            GenerationModel 객체 리스트.
        """
        cache_key = f"history:{user_id}:limit:{limit}"

        # 1. 캐시 확인
        try:
            cached_data = await self.cache_service.get(cache_key)
            if cached_data:
                data = orjson.loads(cached_data)
                return [GenerationModel(**item) for item in data]
        except Exception as e:
            logger.warning(f"History Cache Get Failed: {e}")

        # 2. DB 조회 (동기 함수를 스레드풀에서 실행)
        history = await run_in_threadpool(self._get_user_history_sync, user_id, limit)

        # 3. 캐시 저장
        try:
            # model_dump(mode='json') handles datetime -> ISO string conversion
            serialized = orjson.dumps([m.model_dump(mode="json") for m in history]).decode("utf-8")
            await self.cache_service.set(cache_key, serialized, ttl=3600)
        except Exception as e:
            logger.warning(f"History Cache Set Failed: {e}")

        return history
