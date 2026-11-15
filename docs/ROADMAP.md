# APPROVE — Delivery Roadmap

The roadmap is phase-gated. Completing a phase does not automatically authorize work in the next phase; major design choices and scope changes are reviewed before implementation.

## Phase 0 — Repository foundation and architecture baseline

**Current phase**

- [x] Inspect the initial repository.
- [ ] Establish project overview and contributor conventions.
- [ ] Record architecture, security baseline, and delivery roadmap.
- [ ] Add safe environment and ignore-file templates.
- [ ] Review the baseline before starting implementation.

**Exit criteria:** documentation is internally consistent, secrets are excluded, and the team agrees on the Phase 1 scope.

## Phase 1 — Data model, authentication, and academic administration

- Define the relational schema and migrations.
- Implement secure authentication and role-based authorization.
- Implement administrator-provisioned student/faculty accounts and first-admin bootstrap.
- Implement academic structure and roster import with validation.
- Add backend unit and integration tests.

**Exit criteria:** a clean local environment can create the academic structure, provision pilot accounts, and enforce role boundaries.

## Phase 2 — Faculty portal and manual session workflow

- Build faculty and administrator portal foundations.
- Implement manual session initialization and reusable templates.
- Validate eligible roster, room, subject, section, and session lifecycle.
- Add faculty session dashboard.

**Exit criteria:** faculty can create, inspect, and close a valid session without a fixed timetable.

## Phase 3 — Student application and rotating QR flow

- Build the student application shell and authentication flow.
- Design and implement signed, short-lived, session-bound QR challenges.
- Enforce single-use challenge consumption and replay protection.
- Add initial attendance-attempt lifecycle.

**Exit criteria:** a student can submit a valid challenge and the backend rejects expired, tampered, wrong-session, and replayed challenges.

## Phase 4 — Cryptographic device binding

- Implement device key registration and challenge-response.
- Use Android Keystore and iOS Keychain/Secure Enclave capabilities where supported.
- Implement device revocation and controlled replacement.
- Define explicit unsupported-device behavior.

**Exit criteria:** backend can verify signatures from registered keys and reject revoked or unregistered devices.

## Phase 5 — Android BLE room anchor

- Build the pilot Android anchor app.
- Register an anchor to a classroom.
- Advertise authenticated rotating data during active sessions.
- Add foreground student scanning, freshness validation, and anchor health diagnostics.

**Exit criteria:** backend accepts only fresh evidence from a registered anchor associated with the active room/session. Document relay limitations.

## Phase 6 — Verification engine and faculty review

- Integrate QR, device, and BLE evidence.
- Implement `VERIFIED_PRESENT`, `PENDING_REVIEW`, and `ABSENT` transitions.
- Notify faculty of pending cases.
- Implement reasoned decisions and append-only audit events.

**Exit criteria:** all state transitions and correction paths are covered by tests and produce an auditable history.

## Phase 7 — Reports and operational readiness

- Attendance history and filters.
- CSV/Excel exports.
- Security, integration, and permission tests.
- Deployment, backup, restore, and recovery documentation.
- Hosting-provider selection based on documented cost and compliance comparison.

**Exit criteria:** a repeatable deployment can support a controlled pilot with recoverable data.

## Phase 8 — Pilot evaluation

- Pilot with one section (approximately 30 students).
- Measure successful verification, pending-review rate, false rejection, session setup time, battery impact, and operational reliability.
- Collect faculty/student feedback and document limitations.
- Decide whether to expand or revise the verification protocol.

## Deferred beyond MVP

- CCTV as a separate evidence-provider module.
- ESP32 hardware room-anchor adapter.
- Uniform detection, face recognition, and advanced AI analytics.
- Microservices, Kubernetes, Kafka, or other scale infrastructure unless measured needs justify them.
