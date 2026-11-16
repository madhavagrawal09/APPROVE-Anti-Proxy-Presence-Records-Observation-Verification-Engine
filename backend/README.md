# APPROVE Backend — Phase 1
Requires Python 3.11+ and PostgreSQL 15+.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set unique JWT_SECRET_KEY and DATABASE_URL
alembic upgrade head
python scripts/seed_roles.py
uvicorn app.main:app --reload
```
API docs: http://127.0.0.1:8000/docs — health: http://127.0.0.1:8000/health

Set BOOTSTRAP_ADMIN_EMAIL and BOOTSTRAP_ADMIN_PASSWORD (minimum 16 characters) then run `python scripts/bootstrap_admin.py`. It refuses to create a second administrator.

Roster workbook headers: `enrollment_number`, `full_name`; optional `email`. Preview does not create accounts. Inspect validation results before confirming. Confirmation returns temporary passwords once; transfer them only through a private approved channel and do not retain them in logs.

Run tests with `pytest`. Before a live pilot, add PostgreSQL integration tests, rate limiting, secure credential delivery, preview expiry/ownership enforcement, backup/restore exercises, HTTPS, and secrets management.
