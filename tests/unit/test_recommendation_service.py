# tests/test_recommendation_service.py
from typing import List

import pandas as pd
import pytest

import app.services.recommendation_service as rec_module
from app.services.recommendation_service import RecommendationService


# ---------- Fakes ----------

class FakeDataProcessor:
    def __init__(self):
        self.loaded_files: List[str] = []
        self.cleaned_dfs: List[pd.DataFrame] = []

    def load_data(self, file_name: str) -> pd.DataFrame:
        self.loaded_files.append(file_name)
        if file_name == "movies.csv":
            return pd.DataFrame(
                {
                    "movieId": [1, 2],
                    "title": ["Movie 1", "Movie 2"],
                    "genres": ["Drama", "Comedy"],
                }
            )
        elif file_name == "ratings.csv":
            return pd.DataFrame(
                {
                    "userId": [10, 10, 20],
                    "movieId": [1, 2, 1],
                    "rating": [4.0, 5.0, 3.0],
                }
            )
        else:
            return pd.DataFrame()

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        self.cleaned_dfs.append(df)
        return df  # no-op for tests


class FakeRecommender:
    def __init__(self, movies_df: pd.DataFrame, ratings_df: pd.DataFrame):
        self.movies_df = movies_df
        self.ratings_df = ratings_df
        self.similar_called_with = None
        self.user_recs_called_with = None

    def get_similar_movies(self, movie_id: int, limit: int):
        self.similar_called_with = (movie_id, limit)
        # Must match TopMovieDto fields: movie_id, title, genres, avg_rating, rating_count
        return [
            {
                "movie_id": 1,
                "title": "Similar 1",
                "genres": "Drama",
                "avg_rating": 4.5,
                "rating_count": 50,
            },
            {
                "movie_id": 2,
                "title": "Similar 2",
                "genres": "Comedy",
                "avg_rating": 4.1,
                "rating_count": 30,
            },
        ]

    def get_user_recommendations(self, user_id: int, limit: int):
        self.user_recs_called_with = (user_id, limit)
        return [
            {
                "movie_id": 3,
                "title": "User Rec 1",
                "genres": "Action",
                "avg_rating": 4.7,
                "rating_count": 70,
            }
        ]


# ---------- Fixture to build service with fakes ----------

@pytest.fixture
def recommendation_service(monkeypatch) -> RecommendationService:
    # Patch SimpleRecommender inside recommendation_service module
    monkeypatch.setattr(rec_module, "SimpleRecommender", FakeRecommender)

    dp = FakeDataProcessor()
    service = RecommendationService(data_processor=dp)

    # attach fakes for assertions
    service._fake_dp = dp
    assert isinstance(service._recommender, FakeRecommender)
    return service


# ---------- Tests ----------

def test_recommendation_service_init_wires_dependencies(recommendation_service: RecommendationService):
    dp: FakeDataProcessor = recommendation_service._fake_dp  # type: ignore[attr-defined]
    recommender: FakeRecommender = recommendation_service._recommender  # type: ignore[assignment]

    # load_data for both files called
    assert "movies.csv" in dp.loaded_files
    assert "ratings.csv" in dp.loaded_files

    # clean_data called on both datasets
    assert len(dp.cleaned_dfs) == 2

    # recommender got the cleaned dataframes
    assert isinstance(recommender.movies_df, pd.DataFrame)
    assert isinstance(recommender.ratings_df, pd.DataFrame)
    assert not recommender.movies_df.empty
    assert not recommender.ratings_df.empty


def test_get_similar_movies_maps_to_dtos(recommendation_service: RecommendationService):
    recommender: FakeRecommender = recommendation_service._recommender  # type: ignore[assignment]

    result = recommendation_service.get_similar_movies(movie_id=42, limit=3)

    # Recommender called with correct params
    assert recommender.similar_called_with == (42, 3)

    # DTO mapping
    assert len(result) == 2
    first = result[0]
    assert first.movie_id == 1
    assert first.title == "Similar 1"
    assert first.genres == "Drama"
    assert first.avg_rating == 4.5
    assert first.rating_count == 50


def test_get_user_recommendations_maps_to_dtos(recommendation_service: RecommendationService):
    recommender: FakeRecommender = recommendation_service._recommender  # type: ignore[assignment]

    result = recommendation_service.get_user_recommendations(user_id=99, limit=5)

    # Recommender called with correct params
    assert recommender.user_recs_called_with == (99, 5)

    # DTO mapping
    assert len(result) == 1
    first = result[0]
    assert first.movie_id == 3
    assert first.title == "User Rec 1"
    assert first.genres == "Action"
    assert first.avg_rating == 4.7
    assert first.rating_count == 70
