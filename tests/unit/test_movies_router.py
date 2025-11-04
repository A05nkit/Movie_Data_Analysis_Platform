# tests/test_movies_router.py
from app.api.routers.movies import (
    get_movies_stats,
    get_top_movies,
    get_similar_movies,
)
from app.models.dto import TopMoviesQuery


class FakeAnalysisService:
    def __init__(self):
        self.stats_called = False
        self.top_movies_called_with = None

    def get_movies_dataset_stats(self):
        self.stats_called = True
        return {"row_count": 123, "unique_movies": 10}

    def get_top_movies(self, limit: int, min_ratings: int):
        self.top_movies_called_with = (limit, min_ratings)
        return [
            {
                "movie_id": 1,
                "title": "Top 1",
                "genres": "Drama",
                "avg_rating": 4.8,
                "rating_count": 200,
            }
        ]


class FakeRecommendationService:
    def __init__(self):
        self.similar_called_with = None

    def get_similar_movies(self, movie_id: int, limit: int):
        self.similar_called_with = (movie_id, limit)
        return [
            {
                "movie_id": 2,
                "title": "Similar 1",
                "genres": "Comedy",
                "avg_rating": 4.3,
                "rating_count": 80,
            }
        ]


def test_get_movies_stats_calls_analysis_service():
    service = FakeAnalysisService()

    result = get_movies_stats(service=service)

    assert service.stats_called is True
    assert result["row_count"] == 123
    assert result["unique_movies"] == 10


def test_get_top_movies_calls_analysis_service_with_query():
    service = FakeAnalysisService()
    query = TopMoviesQuery(limit=5, min_ratings=20)

    result = get_top_movies(query=query, service=service)

    assert service.top_movies_called_with == (5, 20)
    assert isinstance(result, list)
    assert result[0]["title"] == "Top 1"


def test_get_similar_movies_calls_recommendation_service():
    service = FakeRecommendationService()

    result = get_similar_movies(movie_id=42, limit=3, service=service)

    assert service.similar_called_with == (42, 3)
    assert isinstance(result, list)
    assert result[0]["movie_id"] == 2
