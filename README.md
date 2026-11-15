# APPROVE

**AI-Powered Participation, Records, Observation & Verification Engine**

APPROVE is a secure, role-based college attendance platform designed to make classroom attendance auditable and more resistant to proxy attendance. The pilot combines short-lived QR challenges, registered-device cryptographic proof, a classroom BLE anchor, and faculty review.

> **Project status:** Phase 0 — repository foundation and architecture baseline. The application is not implemented yet.

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

## Proposed technology

| Layer | Baseline |
| --- | --- |
| Student application | React Native + TypeScript |
| Faculty / administrator portal | React + TypeScript |
| Backend API | Python + FastAPI |
| Primary database | PostgreSQL |
| Short-lived coordination (if needed) | Redis |
| BLE room anchor | Native Android app (Kotlin) for the pilot |
| Backend tests | Pytest |
| API contract | OpenAPI |

This is a modular-monolith starting point. Hosting provider, cloud region, and production topology remain open until cost, data-residency, backup, and institutional requirements are reviewed.

## Documentation

- [Architecture and system boundaries](docs/ARCHITECTURE.md)
- [Security baseline and threat model](docs/SECURITY.md)
- [Delivery roadmap](docs/ROADMAP.md)
- [Contribution and development conventions](CONTRIBUTING.md)

## Repository status

The repository currently contains project documentation and setup conventions. Backend, mobile, portal, database migrations, and BLE-anchor implementation will be added in later approved phases.

## Security notice

APPROVE is intended to raise the cost of attendance fraud, not to claim that proxy attendance is impossible. BLE signal strength is not cryptographic distance proof and can be affected by the environment; relay attacks remain a consideration. Device binding proves possession of a registered key, not the identity of the person holding the device. See the [security baseline](docs/SECURITY.md).

## License

The repository currently contains an Apache-2.0 license template. Its copyright notice still needs to be completed by the repository owner before distribution.
