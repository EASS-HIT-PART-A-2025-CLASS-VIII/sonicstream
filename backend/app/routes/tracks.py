from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional

from ..database import get_db
from ..schemas import TrackResponse, TrackListResponse, SimilarTrackResponse

router = APIRouter(prefix="/tracks", tags=["tracks"])

def row_to_track(row) -> dict:
    """Convert a database row to a track dictionary."""
    return {
        "id": str(row.track_id) if hasattr(row, 'track_id') else str(row.id) if hasattr(row, 'id') else "",
        "name": row.name if hasattr(row, 'name') else "Unknown",
        "artist": row.artist if hasattr(row, 'artist') else "Unknown",
        "album": None,  # Not available in Postgres schema
        "genre": None,
        "duration_ms": None,
        "danceability": float(row.danceability) if hasattr(row, 'danceability') and row.danceability else None,
        "energy": float(row.energy) if hasattr(row, 'energy') and row.energy else None,
        "valence": float(row.valence) if hasattr(row, 'valence') and row.valence else None,
        "tempo": float(row.tempo) if hasattr(row, 'tempo') and row.tempo else None,
        "acousticness": float(row.acousticness) if hasattr(row, 'acousticness') and row.acousticness else None,
        "instrumentalness": None,
        "liveness": None,
        "speechiness": None,
        "loudness": None,
        "cover_url": None,
    }

@router.get("", response_model=TrackListResponse)
async def get_tracks(
    page: int = Query(0, ge=0),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get paginated list of tracks."""
    offset = page * page_size
    
    # Get total count
    count_result = db.execute(text("SELECT COUNT(*) FROM tracks")).fetchone()
    total = count_result[0] if count_result else 0
    
    # Simple query for Postgres (denormalized schema)
    result = db.execute(
        text("""
            SELECT track_id, name, artist, danceability, energy, valence, tempo, acousticness
            FROM tracks
            ORDER BY popularity DESC NULLS LAST
            LIMIT :limit OFFSET :offset
        """),
        {"limit": page_size, "offset": offset}
    ).fetchall()
    
    tracks = [row_to_track(row) for row in result]
    
    return {
        "tracks": tracks,
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_more": offset + page_size < total
    }

@router.get("/trending", response_model=TrackListResponse)
async def get_trending_tracks(
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get trending/popular tracks."""
    result = db.execute(
        text("""
            SELECT track_id, name, artist, danceability, energy, valence, tempo, acousticness
            FROM tracks
            ORDER BY popularity DESC NULLS LAST
            LIMIT :limit
        """),
        {"limit": limit}
    ).fetchall()
    
    tracks = [row_to_track(row) for row in result]
    
    return {
        "tracks": tracks,
        "total": len(tracks),
        "page": 0,
        "page_size": limit,
        "has_more": False
    }

@router.get("/search", response_model=TrackListResponse)
async def search_tracks(
    q: str = Query(..., min_length=1),
    page: int = Query(0, ge=0),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search tracks by name or artist."""
    offset = page * page_size
    search_term = f"%{q}%"
    
    # Search in track names and artist names
    result = db.execute(
        text("""
            SELECT track_id, name, artist, danceability, energy, valence, tempo, acousticness
            FROM tracks
            WHERE name ILIKE :term OR artist ILIKE :term
            ORDER BY popularity DESC NULLS LAST
            LIMIT :limit OFFSET :offset
        """),
        {"term": search_term, "limit": page_size, "offset": offset}
    ).fetchall()
    
    tracks = [row_to_track(row) for row in result]
    
    return {
        "tracks": tracks,
        "total": len(tracks),
        "page": page,
        "page_size": page_size,
        "has_more": len(tracks) == page_size
    }

@router.get("/{track_id}")
async def get_track(track_id: str, db: Session = Depends(get_db)):
    """Get a single track by ID."""
    result = db.execute(
        text("""
            SELECT track_id, name, artist, danceability, energy, valence, tempo, acousticness
            FROM tracks
            WHERE track_id = :id
            LIMIT 1
        """),
        {"id": track_id}
    ).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Track not found")
    
    return row_to_track(result)

@router.get("/{track_id}/similar", response_model=list[SimilarTrackResponse])
async def get_similar_tracks(
    track_id: str,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get similar tracks using vector similarity (pgvector)."""
    # Get the source track's embedding
    source = db.execute(
        text("SELECT audio_embedding FROM tracks WHERE track_id = :id"),
        {"id": track_id}
    ).fetchone()
    
    if not source:
        raise HTTPException(status_code=404, detail="Track not found")
    
    # Use pgvector's <-> operator for L2 distance
    result = db.execute(
        text("""
            SELECT 
                track_id, name, artist, danceability, energy, valence, tempo, acousticness,
                audio_embedding <-> (SELECT audio_embedding FROM tracks WHERE track_id = :id) as distance
            FROM tracks
            WHERE track_id != :id
            ORDER BY audio_embedding <-> (SELECT audio_embedding FROM tracks WHERE track_id = :id)
            LIMIT :limit
        """),
        {"id": track_id, "limit": limit}
    ).fetchall()
    
    similar_tracks = []
    for row in result:
        track = row_to_track(row)
        # Convert distance to similarity (0-1, where 1 is most similar)
        distance = float(row.distance) if hasattr(row, 'distance') and row.distance else 0
        similarity = max(0, 1 - (distance / 2))  # Normalize L2 distance
        track["similarity"] = round(similarity, 3)
        similar_tracks.append(track)
    
    return similar_tracks
