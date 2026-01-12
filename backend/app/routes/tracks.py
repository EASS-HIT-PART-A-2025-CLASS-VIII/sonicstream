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
    return {
        "id": str(row.id) if hasattr(row, 'id') else "",
        "name": row.track_name if hasattr(row, 'track_name') else (row.name if hasattr(row, 'name') else "Unknown"),
        "artist": row.artist_name if hasattr(row, 'artist_name') else "Unknown",
        "album": row.album_name if hasattr(row, 'album_name') else None,
        "genre": None,
        "duration_ms": row.duration if hasattr(row, 'duration') else None,
        "danceability": row.danceability if hasattr(row, 'danceability') else None,
        "energy": row.energy if hasattr(row, 'energy') else None,
        "valence": row.valence if hasattr(row, 'valence') else None,
        "tempo": row.tempo if hasattr(row, 'tempo') else None,
        "acousticness": row.acousticness if hasattr(row, 'acousticness') else None,
        "instrumentalness": row.instrumentalness if hasattr(row, 'instrumentalness') else None,
        "liveness": row.liveness if hasattr(row, 'liveness') else None,
        "speechiness": row.speechiness if hasattr(row, 'speechiness') else None,
        "loudness": row.loudness if hasattr(row, 'loudness') else None,
        "cover_url": None,
    }

@router.get("", response_model=TrackListResponse)
async def get_tracks(
    page: int = Query(0, ge=0),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get paginated list of tracks with artist names."""
    offset = page * page_size
    
    # Get total count (cached after first request typically)
    count_result = db.execute(text("SELECT COUNT(*) FROM tracks")).fetchone()
    total = count_result[0] if count_result else 0
    
    # Optimized query: Use subqueries instead of LEFT JOINs for better performance
    # This fetches the first artist and album for each track
    result = db.execute(
        text("""
            SELECT 
                t.id,
                t.name as track_name,
                t.duration,
                t.popularity,
                (SELECT a.name FROM r_track_artist rta 
                 JOIN artists a ON rta.artist_id = a.id 
                 WHERE rta.track_id = t.id LIMIT 1) as artist_name,
                (SELECT alb.name FROM r_albums_tracks rat 
                 JOIN albums alb ON rat.album_id = alb.id 
                 WHERE rat.track_id = t.id LIMIT 1) as album_name,
                af.danceability,
                af.energy,
                af.valence,
                af.tempo,
                af.acousticness,
                af.instrumentalness,
                af.liveness,
                af.speechiness,
                af.loudness
            FROM tracks t
            LEFT JOIN audio_features af ON t.audio_feature_id = af.id
            ORDER BY t.popularity DESC
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
            SELECT 
                t.id,
                t.name as track_name,
                t.duration,
                t.popularity,
                (SELECT a.name FROM r_track_artist rta 
                 JOIN artists a ON rta.artist_id = a.id 
                 WHERE rta.track_id = t.id LIMIT 1) as artist_name,
                (SELECT alb.name FROM r_albums_tracks rat 
                 JOIN albums alb ON rat.album_id = alb.id 
                 WHERE rat.track_id = t.id LIMIT 1) as album_name,
                af.danceability,
                af.energy,
                af.valence,
                af.tempo,
                af.acousticness
            FROM tracks t
            LEFT JOIN audio_features af ON t.audio_feature_id = af.id
            ORDER BY t.popularity DESC
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
    
    # Search in track names first (faster)
    result = db.execute(
        text("""
            SELECT 
                t.id,
                t.name as track_name,
                t.duration,
                t.popularity,
                (SELECT a.name FROM r_track_artist rta 
                 JOIN artists a ON rta.artist_id = a.id 
                 WHERE rta.track_id = t.id LIMIT 1) as artist_name,
                (SELECT alb.name FROM r_albums_tracks rat 
                 JOIN albums alb ON rat.album_id = alb.id 
                 WHERE rat.track_id = t.id LIMIT 1) as album_name
            FROM tracks t
            WHERE t.name LIKE :term
            ORDER BY t.popularity DESC
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
            SELECT 
                t.id,
                t.name as track_name,
                t.duration,
                t.popularity,
                (SELECT a.name FROM r_track_artist rta 
                 JOIN artists a ON rta.artist_id = a.id 
                 WHERE rta.track_id = t.id LIMIT 1) as artist_name,
                (SELECT alb.name FROM r_albums_tracks rat 
                 JOIN albums alb ON rat.album_id = alb.id 
                 WHERE rat.track_id = t.id LIMIT 1) as album_name,
                af.danceability,
                af.energy,
                af.valence,
                af.tempo,
                af.acousticness,
                af.instrumentalness,
                af.liveness,
                af.speechiness,
                af.loudness
            FROM tracks t
            LEFT JOIN audio_features af ON t.audio_feature_id = af.id
            WHERE t.id = :id
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
    """Get similar tracks based on audio features."""
    # Get the source track
    source = db.execute(
        text("""
            SELECT af.* FROM tracks t
            LEFT JOIN audio_features af ON t.audio_feature_id = af.id
            WHERE t.id = :id
        """),
        {"id": track_id}
    ).fetchone()
    
    if not source:
        raise HTTPException(status_code=404, detail="Track not found")
    
    src_dance = getattr(source, 'danceability', 0.5) or 0.5
    src_energy = getattr(source, 'energy', 0.5) or 0.5
    src_valence = getattr(source, 'valence', 0.5) or 0.5
    src_acoust = getattr(source, 'acousticness', 0.5) or 0.5
    src_tempo = (getattr(source, 'tempo', 120) or 120) / 200
    
    result = db.execute(
        text("""
            SELECT 
                t.id,
                t.name as track_name,
                t.duration,
                (SELECT a.name FROM r_track_artist rta 
                 JOIN artists a ON rta.artist_id = a.id 
                 WHERE rta.track_id = t.id LIMIT 1) as artist_name,
                af.danceability,
                af.energy,
                af.valence,
                af.tempo,
                af.acousticness,
                ABS(COALESCE(af.danceability, 0.5) - :dance) + 
                ABS(COALESCE(af.energy, 0.5) - :energy) + 
                ABS(COALESCE(af.valence, 0.5) - :valence) + 
                ABS(COALESCE(af.acousticness, 0.5) - :acoust) +
                ABS(COALESCE(af.tempo, 120) / 200.0 - :tempo) as distance
            FROM tracks t
            LEFT JOIN audio_features af ON t.audio_feature_id = af.id
            WHERE t.id != :id
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
        distance = row.distance if hasattr(row, 'distance') else 0
        similarity = max(0, 1 - (distance / 5))
        track["similarity"] = round(similarity, 3)
        similar_tracks.append(track)
    
    return similar_tracks
