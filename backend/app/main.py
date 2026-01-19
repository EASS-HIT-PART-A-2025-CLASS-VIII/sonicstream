from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import tracks, auth, recommendations
from .database import get_table_schema
from .users_database import init_users_db

app = FastAPI(
    title="Music Discovery API",
    description="AI-powered music recommendation engine with 8M Spotify tracks",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize users database on startup
@app.on_event("startup")
async def startup_event():
    init_users_db()

# Include routers
app.include_router(tracks.router)
app.include_router(auth.router)
app.include_router(recommendations.router)


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
