# Bolt's Optimization Journal

## 2026-02-14 - [Supabase Client & Quota Caching Optimization]
Learning: In Python, relying on `__init__` for Singleton behavior is flawed because `__new__` handles instance creation, and `__init__` is always called afterward unless overridden carefully. The previous implementation caused the Supabase client to be re-instantiated on every request.
Action: Always implement `__new__` for Singletons to ensure strictly one instance exists. Additionally, critical read-heavy paths (like user quota checks) should be cached in Redis to minimize database latency.

## 2026-02-14 - [Cache Strategy for Time-Bound Quotas]
Learning: Caching time-bound data (e.g., weekly quotas) with simple TTLs is risky because cache expiration doesn't align with business logic boundaries (e.g., Monday reset). A user crossing the boundary might see stale data.
Action: Include the time window identifier (e.g., week start date) in the cache key (`quota:weekly:{user_id}:{date}`) to enforce automatic invalidation at boundaries. Use atomic operations (`INCR`) to prevent race conditions during updates.
