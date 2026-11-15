# APPROVE — Architecture Baseline

**Status:** Approved product baseline; implementation details remain subject to phase-specific design review.

## 1. System context

APPROVE has three primary user-facing clients and one room-side component:

1. **Student app (React Native / TypeScript):** account access, device registration, active-session QR submission, BLE anchor evidence, attendance history, and review status.
2. **Faculty and administrator portal (React / TypeScript):** academic setup, account provisioning, session creation, live attendance monitoring, pending-review decisions, corrections, and exports.
3. **Backend (Python / FastAPI):** authentication, authorization, session lifecycle, challenge issuance, evidence validation, attendance state transitions, audit events, and reporting APIs.
4. **Room anchor (native Android / Kotlin):** advertises authenticated, rotating BLE data for a registered classroom during a session. A dedicated Android phone is the pilot hardware; an ESP32 may implement the same adapter contract later.

PostgreSQL is the system of record. Redis is optional and may be introduced for ephemeral challenge coordination or caching only after the consistency and deployment requirements are clear.

## 2. High-level topology

```text
Student app (Android / iOS) ─────┐
                                │
Faculty / Admin web portal ─────┼── HTTPS / API ── FastAPI modular monolith
                                │                       │
Android BLE room anchor ────────┘                       ├── PostgreSQL
                                                        └── Redis (optional)
```

The BLE anchor does not replace server-side validation. The mobile app submits evidence to the backend, which checks it against the active session, registered anchor, freshness rules, and the student's registered device.

## 3. Architectural decisions

| Concern | Baseline decision | Rationale / open point |
| --- | --- | --- |
| Backend shape | Modular monolith | Easier to build, test, deploy, and operate for a small pilot. |
| API | FastAPI with OpenAPI | Python-first implementation and an explicit API contract. |
| Primary data store | PostgreSQL | Relational integrity for enrollment, sessions, attendance, and audit records. |
| Student client | React Native + TypeScript | Shared Android/iOS product surface. Native modules are required for platform security and BLE behavior. |
| Staff portal | React + TypeScript | Separate staff workflow and responsive browser interface. |
| Room anchor | Kotlin Android app for pilot | Reuses an Android phone; avoids requiring dedicated ESP32 purchases initially. |
| Hosting | Low-cost managed cloud pilot, provider undecided | Compare region, cost, backups, operational burden, and institutional/privacy requirements first. |
| iOS builds | macOS or cloud build runner | The development team's Linux machine cannot provide the standard local Xcode toolchain. |

## 4. Core domain boundaries

The initial domain model is expected to include:

- **Institution structure:** institution, campus, department, branch, academic year, semester, section, building, floor, and room.
- **People and access:** student, faculty, administrator, enrollment, role, account credential, and registered device.
- **Teaching setup:** subject, timetable template, and eligible class roster.
- **Room infrastructure:** room anchor, anchor registration, anchor health, and anchor credential.
- **Attendance:** session, session participant, attendance attempt, verification evidence, attendance record, review action, and attendance correction.
- **Governance:** immutable audit event and notification/outbox event.

The detailed relational schema, indexes, foreign keys, and retention rules will be designed in the database phase before migrations are written.

## 5. Session lifecycle

A faculty member manually initializes each session. A timetable template may prefill details but must never start a session automatically.

Required session attributes:

- branch, semester, and section;
- subject and class title/topic;
- room;
- start time;
- expected duration or explicit manual close;
- eligible student roster.

The server is authoritative for session state and challenge timing. Client clocks are not trusted for expiry decisions.

## 6. Verification sequence

1. Faculty starts a session. The backend records the eligible roster and active room.
2. The backend issues short-lived, rotating, signed QR challenges bound to that session.
3. The student app submits the challenge with proof from its registered device key and current room-anchor evidence.
4. The backend validates session status, challenge signature, expiry, single-use/replay state, device registration, anchor registration, and evidence freshness.
5. Valid evidence produces `VERIFIED_PRESENT`. An attempted but inconclusive or failed verification produces `PENDING_REVIEW`, not an automatic absence.
6. Faculty reviews pending cases and records a reasoned decision.
7. At session close, eligible students with no attendance attempt become `ABSENT`. Permitted later corrections remain auditable.

The exact QR payload, signing algorithm, key rotation, device attestation strategy, BLE advertisement format, nonce handling, and replay-store design require a dedicated protocol design and security review before implementation.

## 7. Attendance and audit invariants

- At most one finalized attendance record per `(session_id, student_id)`.
- Every attendance attempt is attributable to a session, student, and registered device where applicable.
- Failed or inconclusive attempts are not silently converted to absence.
- Every faculty correction records old status, new status, reason, actor, timestamp, session, and student.
- Audit events are append-only at the application level; ordinary correction flows never overwrite history.
- Authorization is checked on the server for every protected operation.
- The server, not the client, determines challenge expiry and final verification outcome.

## 8. Platform constraints

- Android device keys should use Android Keystore where available.
- iOS device keys should use Keychain/Secure Enclave capabilities where available; App Attest may be evaluated as an additional integrity signal.
- Hardware-backed storage and attestation support vary by device and OS version. Unsupported devices need an explicit policy rather than a silent downgrade.
- iOS BLE scanning is constrained by platform lifecycle rules. The MVP should scan during an active, foreground attendance flow and must not promise unrestricted background scanning.
- GPS/geofencing, if later used, is supporting context only—not continuous tracking or authoritative attendance proof.

## 9. Deployment boundary

Local development should be lightweight and reproducible. Production hosting remains unselected pending a documented comparison of:

- deployment and managed PostgreSQL cost;
- India-region availability and data-residency requirements;
- backup retention and point-in-time recovery;
- TLS, secret management, logs, and monitoring;
- institutional approval and applicable privacy obligations;
- export and recovery procedures.

No Kubernetes, Kafka, or microservice split is planned for the pilot.
