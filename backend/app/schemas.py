from pydantic import BaseModel
from typing import Optional

class TrackBase(BaseModel):
    id: str
    name: str
    artist: str
    album: Optional[str] = None
    genre: Optional[str] = None
    duration_ms: Optional[int] = None
    
    # Audio features
    danceability: Optional[float] = None
    energy: Optional[float] = None
    valence: Optional[float] = None
    tempo: Optional[float] = None
    acousticness: Optional[float] = None
    instrumentalness: Optional[float] = None
    liveness: Optional[float] = None
    speechiness: Optional[float] = None
    loudness: Optional[float] = None
    
    class Config:
        from_attributes = True

class TrackResponse(TrackBase):
    cover_url: Optional[str] = None

class TrackListResponse(BaseModel):
    tracks: list[TrackResponse]
    total: int
    page: int
    page_size: int
    has_more: bool

class SimilarTrackResponse(TrackResponse):
    similarity: float
