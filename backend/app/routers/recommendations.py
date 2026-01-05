from fastapi import APIRouter, Depends, HTTPException, Body
import psycopg

from app.schemas import RecommendationResponse, RecommendationRequest
from app.dependencies import get_db
from app.services.recommendation import RecommendationService

router = APIRouter(prefix="/recommend", tags=["Recommendations"])

@router.post("/", response_model=RecommendationResponse)
async def get_recommendations(
    request: RecommendationRequest,
    db: psycopg.AsyncConnection = Depends(get_db)
):
    """
    Get track recommendations based on vector similarity.
    """
    service = RecommendationService(db)
    
    # Check if we should verify track existence first? Service handles getting embedding.
    recommendations = await service.get_recommendations(request.track_id, request.limit)
    
    if not recommendations:
        # If service returns empty list, it *might* mean track not found or just no recs. 
        # Ideally service raises exception or returns None for not found.
        # Let's improve service slightly in next iteration or handle it here if we assume not found.
        # For now, let's assume empty list is valid but if track ID is invalid we might want 404.
        pass

    return RecommendationResponse(
        source_track_id=request.track_id,
        recommendations=recommendations
    )
