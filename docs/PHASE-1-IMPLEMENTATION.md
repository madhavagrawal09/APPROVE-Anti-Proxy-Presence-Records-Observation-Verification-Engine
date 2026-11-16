# APPROVE Phase 1 implementation

Approved: single institution; JWT access tokens and rotating refresh tokens; 15-minute access and 7-day refresh defaults; preview-first Excel import.

Included: backend foundation, SQLAlchemy schema, Alembic baseline, login/refresh/logout/password-change, server-side admin RBAC, academic structure endpoints, faculty provisioning, roster preview/validation/confirmation, role seed and controlled admin bootstrap, unit tests.

Deferred: attendance sessions, QR, device binding, BLE, mobile clients, faculty attendance review, CCTV, hosting.

Before pilot: PostgreSQL integration tests, login/upload rate limits, temporary-credential delivery, preview expiry and ownership checks, stronger audit immutability, backup/restore testing, deployment secrets, and security review. The initial migration is a metadata baseline; future schema changes should use explicit Alembic revisions.
