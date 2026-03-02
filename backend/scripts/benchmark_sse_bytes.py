import timeit
import json
import orjson
from datetime import datetime, timezone

sse_chunk = {'type': 'chunk', 'content': 'def test_something():\n    pass'}

def orjson_dump_sse_chunk_str():
    return f"event: chunk\ndata: {orjson.dumps(sse_chunk).decode('utf-8')}\n\n"

def orjson_dump_sse_chunk_bytes():
    return b"event: chunk\ndata: " + orjson.dumps(sse_chunk) + b"\n\n"

if __name__ == "__main__":
    n = 100000
    print(f"--- Benchmarking SSE Bytes vs Str (x{n}) ---")

    t_str = timeit.timeit(orjson_dump_sse_chunk_str, number=n)
    t_bytes = timeit.timeit(orjson_dump_sse_chunk_bytes, number=n)
    print(f"SSE Chunk Str:     {t_str:.4f}s")
    print(f"SSE Chunk Bytes:   {t_bytes:.4f}s ({t_str/t_bytes:.2f}x faster)")
