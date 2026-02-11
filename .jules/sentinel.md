## 2024-05-22 - Worker Fail-Open Auth
**Vulnerability:** Worker service allowed unauthenticated code execution if `WORKER_AUTH_TOKEN` environment variable was missing (Fail Open).
**Learning:** Defaulting to "Dev mode" by checking for *absence* of a secret is dangerous. It assumes absence means "local dev", but it could mean "misconfigured production".
**Prevention:** Enforce secrets by default (Fail Secure). Use explicit flags (e.g., `DISABLE_WORKER_AUTH=true`) to opt-out of security, rather than implicit opt-out.
