from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import List, Optional

from ..database import get_db

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

class TrackRecommendationRequest(BaseModel):
    track_ids: List[str]  # User's liked track IDs
    limit: int = 12

class TrackResponse(BaseModel):
    id: str
    name: str
    artist: str
    album: Optional[str] = None
    popularity: Optional[int] = None
    score: Optional[float] = None
    reason: Optional[str] = None

class TrackListResponse(BaseModel):
    tracks: List[TrackResponse]
    total: int

def row_to_track(row) -> dict:
    """Convert a database row to a track dictionary."""
    return {
        "id": str(row.track_id) if hasattr(row, 'track_id') else "",
        "name": row.name if hasattr(row, 'name') else "Unknown",
        "artist": row.artist if hasattr(row, 'artist') else "Unknown",
        "album": row.album_id if hasattr(row, 'album_id') else None,
        "popularity": row.popularity if hasattr(row, 'popularity') else 0,
        "score": float(row.score) if hasattr(row, 'score') and row.score else None,
        "reason": None
    }

@router.get("/tracks", response_model=TrackListResponse)
async def get_tracks_selection(
    page: int = Query(0, ge=0),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get paginated list of tracks for selection (ordered by popularity)."""
    offset = page * page_size
    
    count_result = db.execute(text("SELECT COUNT(*) FROM tracks")).fetchone()
    total = count_result[0] if count_result else 0
    
    result = db.execute(
        text("""
            SELECT track_id, name, artist, album_id, popularity
            FROM tracks
            ORDER BY popularity DESC NULLS LAST
            LIMIT :limit OFFSET :offset
        """),
        {"limit": page_size, "offset": offset}
    ).fetchall()
    
    tracks = [row_to_track(row) for row in result]
    
    return {
        "tracks": tracks,
        "total": total
    }

@router.post("/tracks", response_model=TrackListResponse)
async def get_track_recommendations(
    request: TrackRecommendationRequest,
    db: Session = Depends(get_db)
):
    """
    Get track recommendations based on user's liked tracks.
    
    Algorithm:
    1. Compute average embedding of chosen tracks
    2. Find similar tracks using pgvector L2 distance
    3. Boost score for same artist
    """
    if not request.track_ids:
        raise HTTPException(status_code=400, detail="At least one track_id is required")
    
    # Format track IDs for SQL
    track_ids_str = ", ".join([f"'{tid}'" for tid in request.track_ids])
    
    # Step 1: Get the average embedding of liked tracks
    avg_embedding_result = db.execute(
        text(f"""
            SELECT 
                AVG((audio_embedding::real[])[1]) as avg1,
                AVG((audio_embedding::real[])[2]) as avg2,
                AVG((audio_embedding::real[])[3]) as avg3,
                AVG((audio_embedding::real[])[4]) as avg4,
                AVG((audio_embedding::real[])[5]) as avg5,
                STRING_AGG(DISTINCT artist, ', ') as liked_artists
            FROM tracks
            WHERE track_id IN ({track_ids_str})
        """)
    ).fetchone()
    
    if not avg_embedding_result or avg_embedding_result.avg1 is None:
        raise HTTPException(status_code=404, detail="No valid tracks found")
    
    # Build average embedding vector
    avg_embedding = f"[{avg_embedding_result.avg1},{avg_embedding_result.avg2},{avg_embedding_result.avg3},{avg_embedding_result.avg4},{avg_embedding_result.avg5}]"
    liked_artists = avg_embedding_result.liked_artists or ""
    liked_artists_list = [a.strip() for a in liked_artists.split(",")]
    
    # Step 2: Find similar tracks
    # Score = audio_similarity (inverted L2 distance)
    # Filter: Exclude tracks from the same artists as the liked tracks
    
    # Format artist exclusion list for SQL array
    quoted_artists = [f"'%{a}%'" for a in liked_artists_list]
    artists_str = ", ".join(quoted_artists)
    excluded_artists_array = f"ARRAY[{artists_str}]"
    
    result = db.execute(
        text(f"""
            SELECT 
                track_id,name,artist,album_id,popularity,
                -- Audio similarity (inverted L2 distance)
                1.0 / (1.0 + (audio_embedding <-> '{avg_embedding}'::vector)) as score
            FROM tracks
            WHERE track_id NOT IN ({track_ids_str})
            AND NOT (artist ILIKE ANY({excluded_artists_array}))
            ORDER BY score DESC
            LIMIT :limit
        """),
        {"limit": request.limit}
    ).fetchall()
    
    tracks = []
    for row in result:
        track = row_to_track(row)
        # Add reason
        if hasattr(row, 'score') and row.score is not None and row.score > 0.8:
            track["reason"] = "Perfect Match"
        else:
            track["reason"] = "Sonic Match"
        tracks.append(track)
    
    return {
        "tracks": tracks,
        "total": len(tracks)
    }
