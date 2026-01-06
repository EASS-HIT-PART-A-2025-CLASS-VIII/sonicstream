from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
import math

from ..database import get_db
from ..schemas import TrackResponse, TrackListResponse, SimilarTrackResponse

router = APIRouter(prefix="/tracks", tags=["tracks"])

def row_to_track(row) -> dict:
    """Convert a database row to a track dictionary."""
    # Safely get artist name from various possible column names
    artist_name = (
        getattr(row, 'artist_name', None) or 
        getattr(row, 'artists', None) or 
        getattr(row, 'artist', None) or 
        "Unknown"
    )
    cover_url = f"https://ui-avatars.com/api/?name={artist_name.replace(' ', '+')}&background=random&color=fff&size=300"
    
    return {
        "id": str(getattr(row, 'track_id', None) or getattr(row, 'id', '')),
        "name": getattr(row, 'track_name', None) or getattr(row, 'name', 'Unknown'),
        "artist": artist_name,
        "album": getattr(row, 'album_name', None) or getattr(row, 'album', None),
        "genre": getattr(row, 'genre', None) or getattr(row, 'track_genre', None),
        "duration_ms": getattr(row, 'duration_ms', None),
        "danceability": getattr(row, 'danceability', None),
        "energy": getattr(row, 'energy', None),
        "valence": getattr(row, 'valence', None),
        "tempo": getattr(row, 'tempo', None),
        "acousticness": getattr(row, 'acousticness', None),
        "instrumentalness": getattr(row, 'instrumentalness', None),
        "liveness": getattr(row, 'liveness', None),
        "speechiness": getattr(row, 'speechiness', None),
        "loudness": getattr(row, 'loudness', None),
        "cover_url": cover_url,
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
    
    # Get tracks
    result = db.execute(
        text(f"SELECT * FROM tracks LIMIT :limit OFFSET :offset"),
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
    """Get trending/popular tracks (by popularity or random selection)."""
    # Try to get by popularity if column exists, otherwise random
    try:
        result = db.execute(
            text("SELECT * FROM tracks ORDER BY popularity DESC LIMIT :limit"),
            {"limit": limit}
        ).fetchall()
    except:
        result = db.execute(
            text("SELECT * FROM tracks ORDER BY RANDOM() LIMIT :limit"),
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
    
    # Count matching results
    count_result = db.execute(
        text("""
            SELECT COUNT(*) FROM tracks 
            WHERE track_name LIKE :term 
            OR artist_name LIKE :term 
            OR artists LIKE :term
        """),
        {"term": search_term}
    ).fetchone()
    total = count_result[0] if count_result else 0
    
    # Get matching tracks
    result = db.execute(
        text("""
            SELECT * FROM tracks 
            WHERE track_name LIKE :term 
            OR artist_name LIKE :term 
            OR artists LIKE :term
            LIMIT :limit OFFSET :offset
        """),
        {"term": search_term, "limit": page_size, "offset": offset}
    ).fetchall()
    
    tracks = [row_to_track(row) for row in result]
    
    return {
        "tracks": tracks,
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_more": offset + page_size < total
    }

@router.get("/{track_id}")
async def get_track(track_id: str, db: Session = Depends(get_db)):
    """Get a single track by ID."""
    result = db.execute(
        text("SELECT * FROM tracks WHERE track_id = :id OR id = :id LIMIT 1"),
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
    """Get similar tracks based on audio features (KNN)."""
    # Get the source track
    source = db.execute(
        text("SELECT * FROM tracks WHERE track_id = :id OR id = :id LIMIT 1"),
        {"id": track_id}
    ).fetchone()
    
    if not source:
        raise HTTPException(status_code=404, detail="Track not found")
    
    # Get audio features of source track
    src_dance = getattr(source, 'danceability', 0.5) or 0.5
    src_energy = getattr(source, 'energy', 0.5) or 0.5
    src_valence = getattr(source, 'valence', 0.5) or 0.5
    src_acoust = getattr(source, 'acousticness', 0.5) or 0.5
    src_tempo = (getattr(source, 'tempo', 120) or 120) / 200  # Normalize tempo
    
    # Calculate Euclidean distance for similarity (simplified KNN)
    # Note: SQLite doesn't have great math functions, so we use a simple approximation
    result = db.execute(
        text("""
            SELECT *, 
                ABS(COALESCE(danceability, 0.5) - :dance) + 
                ABS(COALESCE(energy, 0.5) - :energy) + 
                ABS(COALESCE(valence, 0.5) - :valence) + 
                ABS(COALESCE(acousticness, 0.5) - :acoust) +
                ABS(COALESCE(tempo, 120) / 200.0 - :tempo) as distance
            FROM tracks 
            WHERE (track_id != :id AND id != :id)
            ORDER BY distance ASC
            LIMIT :limit
        """),
        {
            "id": track_id,
            "dance": src_dance,
            "energy": src_energy,
            "valence": src_valence,
            "acoust": src_acoust,
            "tempo": src_tempo,
            "limit": limit
        }
    ).fetchall()
    
    similar_tracks = []
    for row in result:
        track = row_to_track(row)
        # Convert distance to similarity (0-1, where 1 is most similar)
        distance = row.distance if hasattr(row, 'distance') else 0
        similarity = max(0, 1 - (distance / 5))  # Normalize
        track["similarity"] = round(similarity, 3)
        similar_tracks.append(track)
    
    return similar_tracks
