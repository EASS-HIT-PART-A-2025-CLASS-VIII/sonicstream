from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.dependencies import init_db_pool, close_db_pool

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB Pool
    print("🚀 Backend starting up...")
    await init_db_pool()
    yield
    # Shutdown: Close connections
    print("🛑 Backend shutting down...")
    await close_db_pool()

from app.routers import search, recommendations

app = FastAPI(
    title="Music Discovery API",
    description="Professional Music Recommendation Engine",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(search.router)
app.include_router(recommendations.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "music-discovery-backend"}
