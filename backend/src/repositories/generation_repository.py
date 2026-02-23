from datetime import datetime
from typing import Optional, Union
from uuid import UUID

import orjson
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from src.repositories.base_repository import BaseRepository
from src.services.cache_service import CacheService
from src.services.supabase_service import SupabaseService
from src.utils.logger import get_logger
from src.utils.security import EncryptionService

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
    Redis 캐싱을 적용하여 조회 성능을 최적화하고 DB 부하를 줄입니다.
    """

    def __init__(self, supabase_service: SupabaseService):
        """GenerationRepository 인스턴스를 초기화합니다.

        Args:
            supabase_service: Supabase 서비스 인스턴스.
        """
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
        """생성 이력을 저장합니다 (동기 내부 메서드).

        입력 코드와 생성된 코드는 암호화되어 저장됩니다.
        """
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
        """생성 이력을 저장하고 캐시를 무효화합니다 (비동기).

        Args:
            user_id: 사용자 ID.
            input_code: 사용자 입력 코드.
            generated_code: 생성된 테스트 코드.
            language: 프로그래밍 언어.
            model: 사용된 모델명.

        Returns:
            저장된 GenerationModel 객체 (실패 시 None).
        """
        # 1. DB 저장 (스레드풀에서 실행하여 이벤트 루프 블로킹 방지)
        result = await run_in_threadpool(
            self._create_history_sync,
            user_id,
            input_code,
            generated_code,
            language,
            model,
        )

        # 2. 캐시 무효화 (비동기)
        # 해당 사용자의 모든 히스토리 캐시 삭제 (limit 등 파라미터 무관)
        if result:
            try:
                await self.cache_service.clear(f"history:{user_id}:*")
                logger.debug(f"사용자 {user_id}의 이력 캐시가 무효화되었습니다.")
            except Exception as e:
                logger.warning(f"캐시 무효화 실패 (데이터 일관성 주의): {e}")

        return result

    def _get_user_history_sync(self, user_id: str, limit: int = 50) -> list[GenerationModel]:
        """사용자의 생성 이력을 조회합니다 (동기 내부 메서드).

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
                            user_id=item["user_id"],
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

        Redis 캐시를 우선 확인하고, 없을 경우 DB에서 조회 후 캐싱합니다.

        Args:
            user_id: 사용자 ID.
            limit: 조회할 최대 개수.

        Returns:
            GenerationModel 객체 리스트.
        """
        cache_key = f"history:{user_id}:{limit}"

        # 1. 캐시 확인
        try:
            cached_data = await self.cache_service.get(cache_key)
            if cached_data:
                data_list = orjson.loads(cached_data)
                logger.debug(f"이력 조회 캐시 적중: {cache_key}")
                return [GenerationModel(**item) for item in data_list]
        except Exception as e:
            logger.warning(f"캐시 조회 실패: {e}")

        # 2. DB 조회 (Cache Miss)
        try:
            items = await run_in_threadpool(self._get_user_history_sync, user_id, limit)
        except Exception:
            raise

        # 3. 캐시 저장
        try:
            # Pydantic 모델을 dict 리스트로 변환 (datetime 등 직렬화 처리)
            serialized_data = [item.model_dump(mode="json") for item in items]
            json_str = orjson.dumps(serialized_data).decode()

            # 1시간(3600초) 동안 캐시 유지
            await self.cache_service.set(cache_key, json_str, ttl=3600)
        except Exception as e:
            logger.warning(f"캐시 저장 실패: {e}")

        return items
