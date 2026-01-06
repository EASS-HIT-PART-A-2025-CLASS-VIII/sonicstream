from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import tracks
from .database import get_table_schema

app = FastAPI(
    title="Music Discovery API",
    description="AI-powered music recommendation engine with 8M Spotify tracks",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tracks.router)

@app.get("/")
async def root():
    return {
        "message": "Music Discovery API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/schema")
async def get_schema():
    """Get the database schema for debugging."""
    return get_table_schema()
