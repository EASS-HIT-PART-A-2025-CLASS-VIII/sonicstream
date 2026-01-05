from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to DB (Placeholder)
    print("🚀 Backend starting up...")
    yield
    # Shutdown: Close connections
    print("🛑 Backend shutting down...")

app = FastAPI(
    title="Music Discovery API",
    description="Professional Music Recommendation Engine",
    version="0.1.0",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "music-discovery-backend"}
