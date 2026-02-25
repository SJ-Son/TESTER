import timeit
import json
import orjson
from datetime import datetime, timezone

# Sample Data
log_data = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "level": "INFO",
    "message": "User logged in",
    "logger": "src.auth",
    "trace_id": "12345678-1234-5678-1234-567812345678",
    "context": {"user_id": 1, "ip": "127.0.0.1", "role": "admin"},
    "exception": None
}

sse_chunk = {'type': 'chunk', 'content': 'def test_something():\n    pass'}

sse_error = {
    'type': 'error',
    'code': 'INSUFFICIENT_TOKENS',
    'message': '토큰이 부족합니다.',
    'required': 50,
    'current': 10
}

# Baseline Functions
def json_dump_log():
    return json.dumps(log_data, ensure_ascii=False)

def json_dump_sse_chunk():
    return f"event: chunk\ndata: {json.dumps(sse_chunk)}\n\n"

def json_dump_sse_error():
    return f"event: error\ndata: {json.dumps(sse_error, ensure_ascii=False)}\n\n"

# Optimized Functions
def orjson_dump_log():
    return orjson.dumps(log_data).decode('utf-8')

def orjson_dump_sse_chunk():
    return f"event: chunk\ndata: {orjson.dumps(sse_chunk).decode('utf-8')}\n\n"

def orjson_dump_sse_error():
    return f"event: error\ndata: {orjson.dumps(sse_error).decode('utf-8')}\n\n"

# Benchmarking
if __name__ == "__main__":
    n = 100000

    print(f"--- Benchmarking JSON Serialization (x{n}) ---")

    # Logging
    t_log_base = timeit.timeit(json_dump_log, number=n)
    t_log_opt = timeit.timeit(orjson_dump_log, number=n)
    print(f"Log Structure: {t_log_base:.4f}s -> {t_log_opt:.4f}s ({t_log_base/t_log_opt:.2f}x faster)")

    # SSE Chunk
    t_sse_chunk_base = timeit.timeit(json_dump_sse_chunk, number=n)
    t_sse_chunk_opt = timeit.timeit(orjson_dump_sse_chunk, number=n)
    print(f"SSE Chunk:     {t_sse_chunk_base:.4f}s -> {t_sse_chunk_opt:.4f}s ({t_sse_chunk_base/t_sse_chunk_opt:.2f}x faster)")

    # SSE Error (Korean)
    t_sse_error_base = timeit.timeit(json_dump_sse_error, number=n)
    t_sse_error_opt = timeit.timeit(orjson_dump_sse_error, number=n)
    print(f"SSE Error:     {t_sse_error_base:.4f}s -> {t_sse_error_opt:.4f}s ({t_sse_error_base/t_sse_error_opt:.2f}x faster)")
