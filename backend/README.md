# Music Discovery Backend 🎵

Professional FastAPI backend for the Music Discovery Platform, featuring a scalable vector search engine using PostgreSQL + pgvector.

## 🛠️ Stack
- **Framework**: FastAPI (Python 3.11+)
- **Dependency Management**: `uv`
- **Database**: PostgreSQL 16 + pgvector
- **Processing**: Polars (High-performance DataFrames)
- **Infrastructure**: Docker & Docker Compose

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose

### 1. Start Infrastructure
Run the complete stack (DB, Redis, Backend) with Docker Compose.
**Important:** Run this from the **project root** directory (parent of `backend` and `infra`).

```bash
# If you are in the /backend folder, go back one level:
cd ..

# Start the services
docker-compose -f infra/docker-compose.yml up -d --build
```
The API will be available at: `http://localhost:8000`
Interactive Docs (Swagger): `http://localhost:8000/docs`

### 2. Data Ingestion (Kaggle -> Vector DB)
To populate the database with the 8M track dataset:

**Option A: Running inside Docker (Recommended)**
```bash
# 1. Ensure you have your Kaggle credentials in the infra/docker-compose.yml or .env
# 2. Exec into the backend container
docker exec -it music_discovery_api bash

# 3. Run the ingestion script
uv run scripts/ingest_data.py
```

**Option B: Running Locally**
```bash
cd backend
# Install dependencies
uv sync

# Run script (Requires local Postgres running on localhost:5432)
uv run scripts/ingest_data.py
```

### 3. Running Tests
Tests are built with `pytest`.
```bash
docker exec -it music_discovery_api uv run pytest tests/
```

## 📂 Project Structure
- `/app`: FastAPI application source code.
- `/scripts`: Data engineering tasks (Ingestion, ETL).
- `/tests`: Pytest suite.
- `pyproject.toml`: Modern Python dependency configuration.
