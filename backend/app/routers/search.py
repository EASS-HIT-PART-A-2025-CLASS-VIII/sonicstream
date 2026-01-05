from fastapi import APIRouter, Depends, HTTPException, Query
import psycopg
from typing import List

from app.schemas import SearchResponse
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
