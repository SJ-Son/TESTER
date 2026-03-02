import timeit
import orjson
from datetime import datetime, timezone
from uuid import UUID
from pydantic import BaseModel
from typing import Optional

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

history = [
    GenerationModel(
        id=UUID("12345678-1234-5678-1234-567812345678"),
        user_id="user1",
        input_code="def a(): pass",
        generated_code="def test_a(): pass",
        language="python",
        model="gemini",
        created_at=datetime.now(timezone.utc)
    ) for _ in range(50)
]

def baseline():
    # model_dump(mode='json')이 datetime → ISO 문자열로 자동 변환
    serialized = orjson.dumps([m.model_dump(mode="json") for m in history]).decode("utf-8")
    return serialized

def optimized():
    # orjson OPT_SERIALIZE_DATETIME | OPT_SERIALIZE_UUID
    serialized = orjson.dumps(
        [m.model_dump() for m in history],
        option=orjson.OPT_SERIALIZE_UUID | getattr(orjson, 'OPT_SERIALIZE_DATETIME', getattr(orjson, 'OPT_SERIALIZE_DATACLASS', 0)) | getattr(orjson, 'OPT_NAIVE_UTC', 0)
    ).decode("utf-8")
    return serialized

if __name__ == "__main__":
    n = 10000
    print(f"--- Benchmarking Pydantic History Cache Serialization (x{n}) ---")

    t_base = timeit.timeit(baseline, number=n)
    t_opt = timeit.timeit(optimized, number=n)
    print(f"Baseline:   {t_base:.4f}s")
    print(f"Optimized:  {t_opt:.4f}s ({t_base/t_opt:.2f}x faster)")
