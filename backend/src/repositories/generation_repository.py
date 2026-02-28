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
    user_id: Optional[str] = None
    input_code: str
    generated_code: str
    language: str
    model: str
    status: Optional[str] = "success"
    source_code_embedding: Optional[list[float]] = None
    created_at: Optional[datetime] = None


class GenerationRepository(BaseRepository[GenerationModel]):
    """생성 이력(History) 테이블을 관리하는 레포지토리.

    코드 생성 이력의 저장 및 조회를 담당하며, 데이터 암호화/복호화를 처리합니다.
    """

    def __init__(self, supabase_service: SupabaseService):
        """GenerationRepository 인스턴스를 초기화합니다."""
        super().__init__("generation_history")
        self.model_cls = GenerationModel
        self.encryption = EncryptionService()
        self.cache_service = CacheService()

    def _create_history_sync(
        self,
        user_id: str,
        input_code: str,
        generated_code: str,
        language: str,
        model: str,
        source_code_embedding: Optional[list[float]] = None,
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
                source_code_embedding=source_code_embedding,
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
        source_code_embedding: Optional[list[float]] = None,
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
            source_code_embedding: 저장할 임베딩 벡터.

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
            source_code_embedding,
        )

        # 캐시 버전 증가 (O(1) invalidation)
        try:
            await self.cache_service.incr(f"version:history:{user_id}")
        except Exception as e:
            logger.warning(f"Failed to increment cache version for user {user_id}: {e}")

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

        Redis 캐시를 먼저 확인하고, 없으면 DB에서 조회 후 캐싱합니다.
        캐시 TTL은 1시간(3600초)입니다.
        버전 기반 캐싱을 사용하여 O(1) invalidation을 지원합니다.

        Args:
            user_id: 사용자 ID.
            limit: 조회할 최대 개수 (기본값: 50).

        Returns:
            GenerationModel 객체 리스트.
        """
        version = 0
        try:
            v_str = await self.cache_service.get(f"version:history:{user_id}")
            if v_str:
                version = int(v_str)
        except Exception:
            pass  # 버전 조회 실패 시 0(기본값) 사용

        cache_key = f"history:{user_id}:v:{version}:limit:{limit}"

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
            # model_dump(mode='json')이 datetime → ISO 문자열로 자동 변환
            serialized = orjson.dumps([m.model_dump(mode="json") for m in history]).decode("utf-8")
            await self.cache_service.set(cache_key, serialized, ttl=3600)
        except Exception as e:
            logger.warning(f"History Cache Set Failed: {e}")

        return history

    def _get_similar_sync(
        self, embedding: list[float], limit: int = 2, language: Optional[str] = None
    ) -> list[GenerationModel]:
        """주어진 임베딩과 유사한 성공적인 생성 이력을 RPC를 통해 반환합니다."""
        try:
            # RPC 호출
            response = self.client.rpc(
                "match_successful_generations",
                {"query_embedding": embedding, "match_limit": limit, "p_language": language},
            ).execute()

            history_items = []
            if response.data:
                for item in response.data:
                    try:
                        # 데이터 복호화
                        decrypted_input = self.encryption.decrypt(item["input_code"])
                        decrypted_output = self.encryption.decrypt(item["generated_code"])

                        history_items.append(
                            GenerationModel(
                                input_code=decrypted_input,
                                generated_code=decrypted_output,
                                language=language or "unknown",
                                model="unknown",
                                status="success",
                            )
                        )
                    except Exception as e:
                        logger.warning(f"유사 이력 복호화 실패 (건너뜀): {str(e)}")
                        continue

            return history_items
        except Exception as e:
            logger.error(f"유사 이력 조회 RPC 실패: {e}", exc_info=True)
            return []

    async def get_similar_successful_generations(
        self, embedding: list[float], limit: int = 2, language: Optional[str] = None
    ) -> list[GenerationModel]:
        """주어진 벡터와 유사한 성공 이력을 찾아 반환합니다 (비동기)."""
        if not embedding:
            return []

        return await run_in_threadpool(self._get_similar_sync, embedding, limit, language)
