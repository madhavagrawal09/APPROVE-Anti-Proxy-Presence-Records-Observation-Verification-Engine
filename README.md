# APPROVE

**AI-Powered Participation, Records, Observation & Verification Engine**

APPROVE is a secure, role-based college attendance platform designed to make classroom attendance auditable and more resistant to proxy attendance. The pilot combines short-lived QR challenges, registered-device cryptographic proof, a classroom BLE anchor, and faculty review.

> **Project status:** Phase 1 backend foundation committed. Authentication, academic structure, account provisioning, and preview-first roster import are under development; attendance verification and client applications remain future phases.

## Product goals
- Give faculty control over when a class attendance session starts and ends.
- Support irregular schedules through manual session creation and reusable templates.
- Make attendance evidence layered, time-bound, session-bound, and auditable.
- Keep faculty in control of inconclusive cases and attendance corrections.
- Provide students with a clear record of their attendance and review outcomes.

## Pilot scope
The initial pilot is designed for one section of approximately 30 students.
- Administrator-provisioned student and faculty accounts; no public student registration.
- Faculty-created attendance sessions, with optional reusable templates.
- React Native student application for Android and iOS.
- React faculty/administrator web portal.
- Python FastAPI backend and PostgreSQL database.
- Rotating signed QR challenges, registered-device challenge-response, and an Android-phone BLE room anchor.
- Pending-review workflow, immutable audit events, attendance history, and CSV/Excel export.

CCTV, face recognition, uniform detection, and ESP32 hardware are explicitly deferred from the MVP.

## Technology baseline
| Layer | Technology |
| --- | --- |
| Student application | React Native + TypeScript |
| Faculty / administrator portal | React + TypeScript |
| Backend API | Python + FastAPI |
| ORM / migrations | SQLAlchemy 2.x / Alembic |
| Primary database | PostgreSQL |
| Authentication | JWT access tokens + rotating refresh tokens |
| Password hashing | Argon2id |
| Backend tests | Pytest |
| Short-lived coordination (if needed) | Redis |
| BLE room anchor | Native Android app (Kotlin) for the pilot |

The backend setup guide is in [backend/README.md](backend/README.md). Phase 1 implementation boundaries and remaining hardening are recorded in [docs/PHASE-1-IMPLEMENTATION.md](docs/PHASE-1-IMPLEMENTATION.md).

## Architecture and security
- [Architecture and system boundaries](docs/ARCHITECTURE.md)
- [Security baseline and threat model](docs/SECURITY.md)
- [Delivery roadmap](docs/ROADMAP.md)
- [Contribution and development conventions](CONTRIBUTING.md)

This is a modular-monolith starting point. Hosting provider, cloud region, and production topology remain open until cost, data-residency, backup, and institutional requirements are reviewed.

## Security notice
APPROVE is intended to raise the cost of attendance fraud, not to claim that proxy attendance is impossible. BLE signal strength is not cryptographic distance proof and can be affected by the environment; relay attacks remain a consideration. Device binding proves possession of a registered key, not the identity of the person holding the device. See the [security baseline](docs/SECURITY.md).

## License
The repository currently contains an Apache-2.0 license template. Its copyright notice still needs to be completed by the repository owner before distribution.
