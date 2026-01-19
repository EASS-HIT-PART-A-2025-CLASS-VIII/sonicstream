---
name: dbManage
description: Rigorous database management for SQLite, ensuring consistency, safety, and lack of locks.
---

# Professional Database Management Skill

Database integrity is paramount. 

## 1. Safety Procedures
- **Stop the World**: Before any heavy DB op (seed/reset), ensuring the backend process is stopped is CRITICAL to avoid `database is locked` errors in SQLite.
- **Backup**: If working on production/staging data, create a copy of the `.sqlite` file first.

## 2. Operations (using `uv`)

### Reset & Reseed (The "Fresh Start")
Use this when data is corrupted or schema has drastically changed.
1.  **Lock Check**: Close DB Browser/DBeaver.
2.  **Environment**: Ensure `.env` is loaded (managed by scripts).
3.  **Execute**:
    ```bash
    uv run backend/scripts/seeding/reset_db.py
    uv run backend/scripts/seeding/dev_seed.py
    ```
4.  **Verify**:
    ```bash
    uv run python -c "from sqlmodel import Session, create_engine, select; from backend.app.models import Song; engine = create_engine('sqlite:///spotify_dev.sqlite'); print(f'Songs: {len(Session(engine).exec(select(Song)).all())}')"
    ```

### Schema Migrations
- **Never** modify the DB file manually.
- Use `alembic` (if configured) or the provided `optimize_db.py` for maintenance.
- Run `uv run backend/scripts/etl/optimize_db.py` after bulk inserts to run `VACUUM` and `ANALYZE`.

### Transactions
- When writing custom scripts, ALWAYS use a context manager:
    ```python
    with Session(engine) as session:
        try:
            # operations
            session.commit()
        except Exception:
            session.rollback()
            raise
    ```
