from typing import Any, Generic, Optional, TypeVar

from postgrest.exceptions import APIError
from pydantic import BaseModel
from src.services.supabase_service import SupabaseService
from src.utils.logger import get_logger

logger = get_logger(__name__)

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """Supabase 테이블에 대한 기본 CRUD 작업을 제공하는 레포지토리 클래스.

    Args:
        Generic[ModelType]: 해당 레포지토리에서 다루는 Pydantic 모델 타입.
    """

    def __init__(self, table_name: str):
        """BaseRepository 인스턴스를 초기화합니다.

        Args:
            table_name: Supabase 테이블 이름.
        """
        self.table_name = table_name
        self.client = SupabaseService().client

    def create(self, data: dict[str, Any]) -> dict[str, Any] | None:
        """데이터를 테이블에 생성(삽입)합니다.

        Args:
            data: 저장할 데이터 딕셔너리.

        Returns:
            생성된 데이터 딕셔너리 (실패 시 None).

        Raises:
            APIError: Supabase API 오류 시.
        """
        try:
            response = self.client.table(self.table_name).insert(data).execute()
            if response.data:
                return response.data[0]
            return None
        except APIError as e:
            logger.error(f"데이터 생성 중 오류 ({self.table_name}): {e.message}")
            raise
        except Exception as e:
            logger.error(f"데이터 생성 실패 ({self.table_name}): {e}")
            raise

    def get_by_id(self, id: Any) -> Optional[ModelType]:
        """ID로 조회"""
        response = self.client.table(self.table_name).select("*").eq("id", id).execute()
        if response.data:
            return self.model_cls(**response.data[0])
        return None

    def get_all(self, limit: int = 100) -> list[ModelType]:
        """전체 조회 (Limit 적용)"""
        response = self.client.table(self.table_name).select("*").limit(limit).execute()
        return [self.model_cls(**item) for item in response.data]

    def update(self, id: Any, data: dict) -> Optional[ModelType]:
        """데이터 수정"""
        response = self.client.table(self.table_name).update(data).eq("id", id).execute()
        if response.data:
            return self.model_cls(**response.data[0])
        return None

    def delete(self, id: Any) -> bool:
        """데이터 삭제"""
        self.client.table(self.table_name).delete().eq("id", id).execute()
        return True
