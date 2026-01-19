from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import List, Optional

from ..database import get_db

router = APIRouter(prefix="/albums", tags=["albums"])


# ==================== SCHEMAS ====================

class AlbumResponse(BaseModel):
    id: str
    name: str
    artist: str
    popularity: Optional[int] = None
    genre: Optional[str] = None
    cover_url: Optional[str] = None


class AlbumListResponse(BaseModel):
    albums: List[AlbumResponse]
    total: int


class SimilarAlbumResponse(AlbumResponse):
    similarity: float
    reason: Optional[str] = None


class AlbumRecommendationRequest(BaseModel):
    album_id: str
    limit: int = 10


# ==================== HELPERS ====================

def row_to_album(row) -> dict:
    """Convert a database row to an album dictionary."""
    return {
        "id": str(row.album_id) if hasattr(row, 'album_id') else "",
        "name": row.name if hasattr(row, 'name') else "Unknown",
        "artist": row.artist if hasattr(row, 'artist') else "Unknown",
        "popularity": row.popularity if hasattr(row, 'popularity') else 0,
        "genre": row.genre if hasattr(row, 'genre') else None,
        "cover_url": None,
    }


# ==================== ENDPOINTS ====================

@router.get("/search", response_model=AlbumListResponse)
async def search_albums(
    q: str = Query(..., min_length=1),
    page: int = Query(0, ge=0),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search albums by name or artist."""
    offset = page * page_size
    search_term = f"%{q}%"
    
    result = db.execute(
        text("""
            SELECT album_id, name, artist, popularity, genre
            FROM albums
            WHERE name ILIKE :term OR artist ILIKE :term
            ORDER BY popularity DESC NULLS LAST
            LIMIT :limit OFFSET :offset
        """),
        {"term": search_term, "limit": page_size, "offset": offset}
    ).fetchall()
    
    albums = [row_to_album(row) for row in result]
    
    return {
        "albums": albums,
        "total": len(albums)
    }


@router.get("", response_model=AlbumListResponse)
async def get_albums(
    page: int = Query(0, ge=0),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get paginated list of albums ordered by popularity."""
    offset = page * page_size
    
    count_result = db.execute(text("SELECT COUNT(*) FROM albums")).fetchone()
    total = count_result[0] if count_result else 0
    
    result = db.execute(
        text("""
            SELECT album_id, name, artist, popularity, genre
            FROM albums
            ORDER BY popularity DESC NULLS LAST
            LIMIT :limit OFFSET :offset
        """),
        {"limit": page_size, "offset": offset}
    ).fetchall()
    
    albums = [row_to_album(row) for row in result]
    
    return {
        "albums": albums,
        "total": total
    }


@router.get("/{album_id}", response_model=AlbumResponse)
async def get_album(album_id: str, db: Session = Depends(get_db)):
    """Get a single album by ID."""
    result = db.execute(
        text("""
            SELECT album_id, name, artist, popularity
            FROM albums
            WHERE album_id = :id
            LIMIT 1
        """),
        {"id": album_id}
    ).fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Album not found")
    
    return row_to_album(result)


@router.post("/recommend", response_model=List[SimilarAlbumResponse])
async def get_album_recommendations(
    request: AlbumRecommendationRequest,
    db: Session = Depends(get_db)
):
    """
    Get album recommendations using enhanced K-NN with:
    1. 9D audio feature embeddings (5 base + 4 derived)
    2. Weighted cosine similarity
    3. Genre-based boosting
    4. Asymmetric popularity filtering
    """
    # Verify source album exists and get its details
    source = db.execute(
        text("SELECT avg_embedding, popularity, genre FROM albums WHERE album_id = :id"),
        {"id": request.album_id}
    ).fetchone()
    
    if not source:
        raise HTTPException(status_code=404, detail="Album not found")
    
    source_popularity = source.popularity or 0
    source_genre = source.genre or 'other'
    
    # Asymmetric popularity filter:
    # - If source is popular (>= 50): only recommend albums with popularity >= (source - 40)
    # - This prevents "Linkin Park" (Pop 85) from recommending "Obscure Band" (Pop 10)
    # - But allows "Obscure Band" (Pop 10) to recommend "Linkin Park"
    popularity_threshold = 0
    if source_popularity >= 50:
        popularity_threshold = max(0, source_popularity - 40)
        
    popularity_filter = f"popularity >= {popularity_threshold}"
    
    # K-NN search using cosine similarity (<=> operator)
    result = db.execute(
        text(f"""
            WITH source_album AS (
                SELECT avg_embedding FROM albums WHERE album_id = :id
            ),
            weighted_similarities AS (
                SELECT 
                    album_id, name, artist, popularity, genre,
                    -- Cosine similarity (1 - cosine_distance)
                    1 - (avg_embedding <=> (SELECT avg_embedding FROM source_album)) as base_similarity
                FROM albums
                WHERE album_id != :id
                  AND {popularity_filter}
            )
            SELECT 
                album_id, name, artist, popularity, genre,
                -- Apply subtle genre boost: +0.05 if same genre (avoid saturating at 1.0)
                CASE 
                    WHEN genre = :source_genre THEN base_similarity + 0.05
                    ELSE base_similarity
                END as similarity
            FROM weighted_similarities
            ORDER BY similarity DESC, popularity DESC
            LIMIT :limit
        """),
        {
            "id": request.album_id, 
            "limit": request.limit,
            "source_genre": source_genre
        }
    ).fetchall()
    
    similar_albums = []
    for row in result:
        album = row_to_album(row)
        similarity = float(row.similarity) if hasattr(row, 'similarity') and row.similarity else 0
        
        # Clamp similarity to [0, 1]
        similarity = max(0, min(1, similarity))
        album["similarity"] = round(similarity, 3)
        
        # Generate reason based on similarity score and genre match
        genre_match = hasattr(row, 'genre') and row.genre == source_genre
        if similarity > 0.9:
            album["reason"] = "Perfect Match" + (" • Same Genre" if genre_match else "")
        elif similarity > 0.75:
            album["reason"] = "Very Similar" + (" • Same Genre" if genre_match else "")
        elif similarity > 0.6:
            album["reason"] = "Similar Vibes" + (" • Same Genre" if genre_match else "")
        else:
            album["reason"] = "You Might Like"
        
        similar_albums.append(album)
    
    return similar_albums
