from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel

from backend.src.services.supabase_service import SupabaseService

T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    """Supabase 기반 Generic Repository"""

    def __init__(self, supabase_service: SupabaseService, table_name: str, model_cls: type[T]):
        self.client = supabase_service.client
        self.table_name = table_name
        self.model_cls = model_cls

    def create(self, data: T) -> Optional[T]:
        """데이터 생성"""
        try:
            response = self.client.table(self.table_name).insert(data.model_dump()).execute()
            if response.data:
                return self.model_cls(**response.data[0])
            return None
        except Exception as e:
            raise e

    def get_by_id(self, id: Any) -> Optional[T]:
        """ID로 조회"""
        try:
            response = self.client.table(self.table_name).select("*").eq("id", id).execute()
            if response.data:
                return self.model_cls(**response.data[0])
            return None
        except Exception:
            return None

    def get_all(self, limit: int = 100) -> list[T]:
        """전체 조회 (Limit 적용)"""
        try:
            response = self.client.table(self.table_name).select("*").limit(limit).execute()
            return [self.model_cls(**item) for item in response.data]
        except Exception:
            return []

    def update(self, id: Any, data: dict) -> Optional[T]:
        """데이터 수정"""
        try:
            response = self.client.table(self.table_name).update(data).eq("id", id).execute()
            if response.data:
                return self.model_cls(**response.data[0])
            return None
        except Exception:
            return None

    def delete(self, id: Any) -> bool:
        """데이터 삭제"""
        try:
            self.client.table(self.table_name).delete().eq("id", id).execute()
            return True
        except Exception:
            return False
