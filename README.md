# Invictus Backend

FastAPI and PostgreSQL API for **Invictus — Unconquered. Always Forward.**

## Development

```bash
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt
copy .env.example .env
.venv/Scripts/alembic upgrade head
.venv/Scripts/uvicorn app.main:app --reload
```

Use `DATA_PROVIDER=memory` for an offline demo or `DATA_PROVIDER=postgres` with the Supabase Session Pooler connection string. Never commit `.env`.

## Tests

```bash
.venv/Scripts/python -m pytest -q
```
