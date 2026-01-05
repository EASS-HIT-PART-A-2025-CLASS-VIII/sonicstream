from fastapi import APIRouter, Depends, HTTPException, Query
import psycopg
from typing import List

from app.schemas import SearchResponse, Track
from app.dependencies import get_db
from app.services.search import SearchService

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("/", response_model=SearchResponse)
async def search_tracks(
    q: str = Query(..., min_length=2, description="Search query for track name or artist"),
    limit: int = Query(10, ge=1, le=50),
    db: psycopg.AsyncConnection = Depends(get_db)
):
    """
    Search for tracks by name or artist (fuzzy match).
    """
    service = SearchService(db)
    results = await service.search_tracks(q, limit)
    return SearchResponse(results=results)

@router.get("/debug/tracks", response_model=SearchResponse)
async def get_debug_tracks(
    limit: int = 10,
    db: psycopg.AsyncConnection = Depends(get_db)
):
    """
    DEBUG: Get random tracks to verify database content.
    """
    async with db.cursor() as cur:
        await cur.execute("""
            SELECT track_id, name, artist, danceability, energy, valence, tempo, acousticness
            FROM tracks
            LIMIT %s
        """, (limit,))
        rows = await cur.fetchall()
        
        tracks = [
            Track(
                track_id=row[0],
                name=row[1],
                artist=row[2],
                danceability=row[3],
                energy=row[4],
                valence=row[5],
                tempo=row[6],
                acousticness=row[7]
            ) for row in rows
        ]
        return SearchResponse(results=tracks)
