from app.api.routers.users import (
    get_user_stats,
    get_user_recommendations,
)
from app.models.dto import RecommendationQuery


class FakeAnalysisService:
    def __init__(self):
        self.called_with = None

    def get_user_statistics(self, user_id: int):
        self.called_with = user_id
        # Shape doesn't matter here; FastAPI response_model is not applied
        # when we call the function directly.
        return {"user_id": user_id, "total_ratings": 5, "average_rating": 4.2}


class FakeRecommendationService:
    def __init__(self):
        self.called_with = None

    def get_user_recommendations(self, user_id: int, limit: int):
        self.called_with = (user_id, limit)
        return [
            {
                "movie_id": 1,
                "title": "Dummy Movie",
                "average_rating": 4.5,
                "rating_count": 100,
            }
        ]


def test_get_user_stats_calls_analysis_service():
    service = FakeAnalysisService()

    result = get_user_stats(user_id=42, service=service)

    assert service.called_with == 42
    assert result["user_id"] == 42
    assert "total_ratings" in result


def test_get_user_recommendations_calls_recommendation_service():
    service = FakeRecommendationService()
    query = RecommendationQuery(limit=3)

    result = get_user_recommendations(
        user_id=7,
        query=query,
        service=service,
    )

    assert service.called_with == (7, 3)
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["title"] == "Dummy Movie"
