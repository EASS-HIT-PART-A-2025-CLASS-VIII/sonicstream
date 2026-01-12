# Music Discovery Backend 🎵

Professional FastAPI backend for the Music Discovery Platform, featuring a scalable vector search engine using PostgreSQL + pgvector.

## 🛠️ Stack
- **Framework**: FastAPI (Python 3.11+)
- **Dependency Management**: `uv` (local) / `pip` (Docker)
- **Database**: PostgreSQL 16 + pgvector
- **Processing**: Polars (High-performance DataFrames)
- **Infrastructure**: Docker & Docker Compose

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose

### 1. Start All Services
Run from the **project root** (where `docker-compose.yml` is):
```bash
docker compose up -d --build
```
This starts:
- `db` (Postgres + pgvector) on port `5432`
- `redis` on port `6379`
- `backend` (FastAPI) on port `8001`
- `frontend` (Next.js) on port `3000`

### 2. Seed the Database (First Time Only)
```bash
docker exec -it music_discovery_backend python scripts/dev_seed.py
```
This loads **10,000 real tracks** from the Spotify dataset into Postgres. You only need to do this once—data persists across restarts.

### 3. Access the App
- **API Docs (Swagger)**: http://localhost:8001/docs
- **Frontend**: http://localhost:3000

---

## 📂 Utility Scripts

| Script | Purpose | How to Run |
|--------|---------|------------|
| `scripts/dev_seed.py` | Seed 10k real rows into Postgres | `docker exec -it music_discovery_backend python scripts/dev_seed.py` |
| `scripts/reset_db.py` | Truncate all data from Postgres | `docker exec -it music_discovery_backend python scripts/reset_db.py` |
| `scripts/create_dev_db.py` | Create a portable `spotify_dev.sqlite` file | `python scripts/create_dev_db.py` (run on host) |

---

## 💾 Data Persistence

| Action | Is Data Lost? |
|--------|---------------|
| `docker compose stop` | ❌ No |
| `docker compose down` | ❌ No |
| Restart your computer | ❌ No |
| `docker compose down -v` | ✅ **Yes** (volumes deleted) |

---

## 🏗️ Architecture
The backend is structured vertically by domain:
- `app/routers`: API Endpoints (Controllers).
- `app/services`: Business Logic & DB Interactions.
- `app/schemas`: Pydantic Models (DTOs).
- `app/dependencies`: Dependency Injection (DB Pool).

## 🔌 API Endpoints
### Tracks
- **GET /tracks**: Paginated list of all tracks.
- **GET /tracks/search?q=...**: Fuzzy text search by name or artist.
- **GET /tracks/{id}/similar**: Find similar tracks using vector similarity.

---

## 📁 Project Structure
- `/app`: FastAPI application source code.
- `/scripts`: Data engineering tasks (Seeding, Reset, ETL).
- `/tests`: Pytest suite (Unit & Mock Integration).
- `pyproject.toml`: Modern Python dependency configuration.
- `requirements.txt`: Legacy pip dependencies (used by Dockerfile).
