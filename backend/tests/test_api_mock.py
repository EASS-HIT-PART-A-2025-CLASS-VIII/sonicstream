import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app
from app.dependencies import get_db
from app.schemas import Track

# Mock the DB dependency
async def override_get_db():
    mock_conn = AsyncMock()
    yield mock_conn

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Sample Track Data
SAMPLE_TRACK = Track(
    track_id="t1",
    name="Test Song",
    artist="Test Artist",
    danceability=0.8,
    energy=0.7,
    valence=0.9,
    tempo=120.0,
    acousticness=0.1
)

@pytest.fixture
def mock_search_service():
    with patch("app.routers.search.SearchService") as MockService:
        instance = MockService.return_value
        instance.search_tracks = AsyncMock(return_value=[SAMPLE_TRACK])
        yield instance

@pytest.fixture
def mock_recommendation_service():
    with patch("app.routers.recommendations.RecommendationService") as MockService:
        instance = MockService.return_value
        instance.get_recommendations = AsyncMock(return_value=[SAMPLE_TRACK])
        yield instance

def test_health_check():
    """Verifies health endpoint is reachable."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_search_endpoint(mock_search_service):
    """Verifies that the search endpoint returns results correctly."""
    response = client.get("/search/?q=Test")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 1
    assert data["results"][0]["name"] == "Test Song"
    
    # Verify validation
    response_invalid = client.get("/search/?q=a") # Too short
    assert response_invalid.status_code == 422 

def test_recommendation_endpoint(mock_recommendation_service):
    """Verifies that the recommendation endpoint accepts ID and returns tracks."""
    payload = {"track_id": "t1", "limit": 5}
    response = client.post("/recommend/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["source_track_id"] == "t1"
    assert len(data["recommendations"]) == 1
    assert data["recommendations"][0]["track_id"] == "t1"

