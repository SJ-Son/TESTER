import time
import json
import orjson

def benchmark_log_serialization(iterations=100_000):
    log_data = {
        "timestamp": "2023-10-27T10:00:00.123456+00:00",
        "level": "INFO",
        "message": "테스트 코드 생성 요청",
        "logger": "src.api.v1.generator",
        "trace_id": "12345678-1234-5678-1234-567812345678",
        "context": {
            "user_id": "user_123",
            "language": "python",
            "model": "gemini-pro"
        }
    }

    print(f"\n[Logging Benchmark] iterations={iterations}")

    # Standard json
    start = time.time()
    for _ in range(iterations):
        json.dumps(log_data, ensure_ascii=False)
    json_duration = time.time() - start
    print(f"json.dumps: {json_duration:.4f}s")

    # orjson
    start = time.time()
    for _ in range(iterations):
        orjson.dumps(log_data).decode('utf-8')
    orjson_duration = time.time() - start
    print(f"orjson.dumps: {orjson_duration:.4f}s")

    improvement = (json_duration - orjson_duration) / json_duration * 100
    print(f"Improvement: {improvement:.2f}%")


def benchmark_sse_chunk(iterations=100_000):
    chunk_data = {"type": "chunk", "content": "import pytest\n\ndef test_example():\n    pass"}

    print(f"\n[SSE Chunk Benchmark] iterations={iterations}")

    # Standard json
    start = time.time()
    for _ in range(iterations):
        json.dumps(chunk_data)
    json_duration = time.time() - start
    print(f"json.dumps: {json_duration:.4f}s")

    # orjson
    start = time.time()
    for _ in range(iterations):
        orjson.dumps(chunk_data).decode('utf-8')
    orjson_duration = time.time() - start
    print(f"orjson.dumps: {orjson_duration:.4f}s")

    improvement = (json_duration - orjson_duration) / json_duration * 100
    print(f"Improvement: {improvement:.2f}%")

if __name__ == "__main__":
    benchmark_log_serialization()
    benchmark_sse_chunk()
