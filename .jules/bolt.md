## 2026-02-08 - Redis Connection Pooling
**Learning:** Instantiating `redis.from_url` (and PINGing) on every request creates significant latency and resource overhead, even with internal connection pooling, because new pool objects are created.
**Action:** Use a module-level singleton or dependency injection with `lru_cache` to reuse the Redis client instance across requests.
