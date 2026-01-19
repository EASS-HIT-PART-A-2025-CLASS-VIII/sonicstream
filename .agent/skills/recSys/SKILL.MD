---
name: recSys
description: Framework for implementing swappable, testable recommendation algorithms using the Strategy Pattern.
---

# Recommendation System Skill

To maintain a professional, scalable architecture, all recommendation logic must strictly follow the **Strategy Pattern**.

## 1. Core Architecture
**NEVER** hardcode SQL or logic inside the Service/Router.

### The Interface
Every algorithm must implement this contract:
```python
from abc import ABC, abstractmethod
from typing import List

class RecommendationStrategy(ABC):
    @abstractmethod
    async def recommend(self, user_id: str, limit: int = 10) -> List[str]:
        """Returns a list of Track IDs"""
        pass
        
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for logging/ab-testing"""
        pass
```

## 2. Implementation Rules
1.  **Isolation**: Strategies must be in `backend/app/recommendations/strategies/`.
2.  **Statelessness**: Algorithms should be stateless class instances.
3.  **Data Abstraction**: Do not assume `pgvector` exists unless the strategy is explicitly `VectorStrategy`. Provide a fallback (e.g., `RandomStrategy` or `TrendingStrategy`).

## 3. The Factory
Use a Factory to instantiate the correct strategy based on configuration or A/B test flags.

```python
class RecommenderFactory:
    @staticmethod
    def get_strategy(mode: str) -> RecommendationStrategy:
        if mode == "vector": return VectorStrategy()
        if mode == "trending": return TrendingStrategy()
        return RandomStrategy()
```

## 4. Evaluation (Professional Standard)
Every new strategy requires a **Offline Metric Test**:
-   **Recall@K**: How many relevant items were in the top K?
-   **Diversity**: Are the results too similar?
-   **Latency**: Must return in < 200ms.

## 5. Development Workflow
1.  Create `strategies/MyNewAlgo.py`.
2.  Implement `recommend()`.
3.  Add entry to `RecommenderFactory`.
4.  Write a test ensuring it returns `limit` items and handles invalid users gracefully.
