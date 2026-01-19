---
name: recSys
description: Principal-grade framework for recommendation engines (Ranking, Context, Resilience).
---

# Principal Recommendation System Skill

## Core Philosophy
We do not just "return items". We **Rank Candidates** based on **Context**.

## 1. The Data Contracts
**NEVER** use raw primitives. Use Domain Models.

```python
from pydantic import BaseModel
from typing import List, Optional, Dict

class RecommendationContext(BaseModel):
    user_id: str
    session_id: str
    timestamp: float
    current_track_id: Optional[str] = None
    device_type: str = "mobile" # mobile, web, speaker

class RecommendationCandidate(BaseModel):
    track_id: str
    score: float # 0.0 to 1.0
    strategy_source: str # e.g. "vector_v1", "trending"
    reason: str # "Similar to [Track Name]"
    debug_info: Optional[Dict] = None # For internal tools ONLY
```

## 2. The Strategy Interface
```python
from abc import ABC, abstractmethod

class RecommendationStrategy(ABC):
    @abstractmethod
    async def recommend(self, ctx: RecommendationContext, limit: int = 100) -> List[RecommendationCandidate]:
        """
        Retrieves CANDIDATES. 
        Note: Limits should be higher (e.g. 100) to allow the Ranker to work.
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier"""
        pass
```

## 3. The Pipeline (Principal Feature)
A professional system separates **Retrieval** from **Ranking**.

1.  **Retrieval layer**: Fast. Gets ~500 candidates. (Vector Search, Trending).
2.  **Filtering layer**: Removes blocked artists, already played tracks.
3.  **Ranking layer**: Heavy. Re-scores top 50 based on business logic.

```python
# Example Pipeline Logic
async def get_recommendations(ctx: RecommendationContext) -> List[RecommendationCandidate]:
    try:
        # 1. Retrieval (With Circuit Breaker)
        candidates = await vector_strategy.recommend(ctx, limit=100)
    except TimeoutError:
        # FALLBACK (Resilience)
        candidates = await trending_strategy.recommend(ctx, limit=100)

    # 2. Ranking
    ranked = ranker.sort(candidates, user_preferences=...)
    
    return ranked[:10]
```

## 4. Observability Requirement
Every response MUST include a `trace_id` in the logs.
If `ctx.user_id` is an internal admin, return `debug_info` in the API response.
