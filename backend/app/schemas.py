from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class Track(BaseModel):
    """
    Represents a music track with its audio features.
    """
    track_id: str
    name: str
    artist: str
    danceability: float
    energy: float
    valence: float
    tempo: float
    acousticness: float
    # We might not need to expose the raw embedding in API responses, keeping it lightweight
    
    model_config = ConfigDict(from_attributes=True)

class RecommendationRequest(BaseModel):
    track_id: str
    limit: int = 10

class SearchRequest(BaseModel):
    query: str
    limit: int = 10

class SearchResponse(BaseModel):
    results: List[Track]

class RecommendationResponse(BaseModel):
    source_track_id: str
    recommendations: List[Track]
