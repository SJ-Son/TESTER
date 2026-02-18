"""JSON 직렬화 성능 측정 스크립트.

표준 json 라이브러리와 orjson 라이브러리의 직렬화 속도를 비교합니다.
"""

import json
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List

import orjson


def measure_serialization() -> None:
    """대용량 데이터에 대한 직렬화 성능을 측정하고 비교 결과를 출력합니다."""
    # Simulate a large payload (History Items)
    payload: List[Dict[str, Any]] = []
    for i in range(50):  # Default limit is 50
        payload.append({
            "id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "input_code": "def hello():\n    print('world')\n" * 100, # Simulate moderate size code
            "generated_code": "class TestHello(unittest.TestCase):\n    def test_hello(self):\n        pass\n" * 100,
            "language": "python",
            "model": "gemini-pro",
            "created_at": datetime.now().isoformat()
        })

    print(f"Payload size: {len(payload)} items")

    # Measure standard JSON
    start_time = time.time()
    for _ in range(100):
        json.dumps(payload)
    json_duration = time.time() - start_time
    print(f"Standard JSON (100 iterations): {json_duration:.4f}s")

    # Measure ORJSON
    start_time = time.time()
    for _ in range(100):
        orjson.dumps(payload)
    orjson_duration = time.time() - start_time
    print(f"ORJSON (100 iterations): {orjson_duration:.4f}s")

    if orjson_duration > 0:
        improvement = json_duration / orjson_duration
        print(f"Speedup: {improvement:.2f}x")
    else:
        print("ORJSON was too fast to measure properly.")

if __name__ == "__main__":
    measure_serialization()
