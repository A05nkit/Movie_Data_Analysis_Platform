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
        self.validated_movies = False
        self.validated_ratings = False

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

    def validate_movies(self, movies_df: pd.DataFrame) -> None:
        self.validated_movies = True

    def validate_ratings(self, ratings_df: pd.DataFrame, movies_df: pd.DataFrame) -> None:
        self.validated_ratings = True


class FakeRecommender:
    def __init__(self, movies_df: pd.DataFrame, ratings_df: pd.DataFrame):
        self.movies_df = movies_df
        self.ratings_df = ratings_df
        self.similar_called_with = None
        self.user_recs_called_with = None

    def get_similar_movies(self, movie_id: int, limit: int):
        self.similar_called_with = (movie_id, limit)
        return [
            {
                "movie_id": 1,
                "title": "Similar 1",
                "genres": "Drama",
                "avg_rating": 4.5,
                "rating_count": 50,
            }
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


# ---------- Fixture ----------

@pytest.fixture
def recommendation_service(monkeypatch) -> RecommendationService:
    # Patch SimpleRecommender with fake
    monkeypatch.setattr(rec_module, "SimpleRecommender", FakeRecommender)

    dp = FakeDataProcessor()
    service = RecommendationService(data_processor=dp)

    # attach for assertions
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

    # validations executed
    assert dp.validated_movies is True
    assert dp.validated_ratings is True

    # recommender got the cleaned dataframes
    assert isinstance(recommender.movies_df, pd.DataFrame)
    assert isinstance(recommender.ratings_df, pd.DataFrame)
    assert not recommender.movies_df.empty
    assert not recommender.ratings_df.empty


def test_public_methods_execute_and_return_dtos(recommendation_service: RecommendationService):
    """Covers get_similar_movies + get_user_recommendations for full coverage."""
    rec = recommendation_service

    sim = rec.get_similar_movies(movie_id=42, limit=2)
    user_recs = rec.get_user_recommendations(user_id=10, limit=3)

    assert sim[0].movie_id == 1
    assert sim[0].title == "Similar 1"
    assert user_recs[0].movie_id == 3
    assert user_recs[0].title == "User Rec 1"
