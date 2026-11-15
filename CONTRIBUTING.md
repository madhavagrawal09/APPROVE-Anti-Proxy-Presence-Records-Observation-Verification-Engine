# Contributing to APPROVE

## Working principles

- Keep changes within the currently approved phase.
- Prefer small, reviewable changes with tests and clear documentation.
- Do not introduce secrets, student records, real credentials, or production data into Git.
- Do not claim a security guarantee that the implementation has not demonstrated.
- Record consequential architecture changes in the documentation and obtain team approval before implementation.

## Branch and commit conventions

Use a short-lived feature branch for implementation work. Suggested branch names:

- `phase-1/database-foundation`
- `phase-1/authentication`
- `phase-2/faculty-sessions`
- `fix/qr-replay-validation`
- `docs/security-review`

Use clear imperative commit messages, for example:

- `docs: establish architecture baseline`
- `feat(api): add session creation endpoint`
- `test(api): cover challenge replay rejection`

Do not force-push shared branches. Review diffs before merging.

## Local development

The intended backend toolchain is Python, FastAPI, PostgreSQL, and Pytest. The web and mobile clients use TypeScript. Exact dependency versions and lockfiles will be added in the phase that introduces each application.

1. Install Git, Python, Node.js, and the relevant platform tools.
2. Clone the repository and open it in VS Code.
3. Copy `.env.example` to a private `.env` and replace placeholders locally.
4. Never commit `.env`, credentials, signing keys, database dumps, or student roster files.
5. Follow the setup instructions added with each implementation phase.

## Quality expectations

- Add tests for business rules, authorization, and security-sensitive behavior.
- Validate input at API boundaries.
- Keep server-side authorization authoritative.
- Use database constraints for invariants that must survive concurrent requests.
- Document configuration and operational assumptions.
- Treat failed or inconclusive attendance evidence as a review case, not as proof of absence.

## Pull request checklist

- [ ] Scope matches the approved phase.
- [ ] Tests added or updated.
- [ ] No secrets or personal data included.
- [ ] Authorization and audit implications reviewed.
- [ ] Documentation updated.
- [ ] Security limitations described accurately.
