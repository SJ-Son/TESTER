## 2025-02-18 - [Information Leakage in Error Responses]
**Vulnerability:** Global exception handlers and SSE streaming endpoints were returning `str(exc)` directly to the client, potentially exposing sensitive internal details (e.g., database connection strings, stack traces).
**Learning:** Default error handling patterns often leak implementation details. `TestClient` raises exceptions by default, which can mask this behavior during testing unless `raise_server_exceptions=False` is used.
**Prevention:** Always use generic error messages for client responses and log the detailed exception internally. Ensure tests explicitly verify error response content for sensitive data leakage.
