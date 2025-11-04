# tests/test_analysis_service.py
from datetime import date
from typing import Any, Dict, List

import pandas as pd
import pytest

import app.services.analysis_service as analysis_module
from app.services.analysis_service import AnalysisService


# ---------- Fakes ----------

class FakeDataProcessor:
    def __init__(self):
        self.loaded_files: List[str] = []
        self.validated_movies = False
        self.validated_ratings = False
        self.stats_called_with = None

    def load_data(self, file_name: str) -> pd.DataFrame:
        self.loaded_files.append(file_name)
        if file_name == "movies.csv":
            return pd.DataFrame(
                {
                    "movieId": [1, 2],
                    "title": ["A", "B"],
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
        # For testing, just return the df unchanged
        return df

    def validate_movies(self, movies_df: pd.DataFrame) -> None:
        self.validated_movies = True

    def validate_ratings(self, ratings_df: pd.DataFrame, movies_df: pd.DataFrame) -> None:
        self.validated_ratings = True

    def aggregate_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        self.stats_called_with = df
        return {"row_count": len(df)}


class FakeMovieAnalyzer:
    def __init__(self, movies_df: pd.DataFrame, ratings_df: pd.DataFrame):
        self.movies_df = movies_df
        self.ratings_df = ratings_df
        self.get_top_movies_called_with = None
        self.analyze_genre_trends_called = False
        self.get_user_statistics_called_with = None
        self.time_series_called = False

    def get_top_movies(self, limit: int, min_ratings: int):
        self.get_top_movies_called_with = (limit, min_ratings)
        # Keys must match TopMovieDto fields: movie_id, title, genres, avg_rating, rating_count
        return [
            {
                "movie_id": 1,
                "title": "Movie 1",
                "genres": "Drama",
                "avg_rating": 4.5,
                "rating_count": 100,
            },
            {
                "movie_id": 2,
                "title": "Movie 2",
                "genres": "Comedy",
                "avg_rating": 4.2,
                "rating_count": 80,
            },
        ]

    def analyze_genre_trends(self):
        self.analyze_genre_trends_called = True
        # Keys must match GenreTrendDto fields: genre, avg_rating, rating_count
        return {
            "genres": [
                {
                    "genre": "Drama",
                    "avg_rating": 4.3,
                    "rating_count": 50,
                },
                {
                    "genre": "Comedy",
                    "avg_rating": 4.0,
                    "rating_count": 30,
                },
            ]
        }

    def get_user_statistics(self, user_id: int):
        self.get_user_statistics_called_with = user_id
        # Keys must match UserStatsDto fields: user_id, avg_rating, rating_count,
        # rating_distribution, genre_preferences (and maybe more, but these are required).
        return {
            "user_id": user_id,
            "avg_rating": 4.1,
            "rating_count": 5,
            "rating_distribution": {
                "1.0": 1,
                "2.0": 2,
                "3.0": 2,
            },
            "genre_preferences": [
                {"genre": "Drama", "avg_rating": 4.3},
                {"genre": "Comedy", "avg_rating": 3.9},
            ],
        }

    def generate_time_series_analysis(self):
        self.time_series_called = True
        return {
            "time_series": [
                {
                    "date": date(2020, 1, 1),
                    "avg_rating": 4.25,
                    "rating_count": 10,
                },
                {
                    "date": date(2020, 1, 2),
                    "avg_rating": 3.75,
                    "rating_count": 5,
                },
            ]
        }


# ---------- Fixture to build AnalysisService with fakes ----------

@pytest.fixture
def analysis_service(monkeypatch) -> AnalysisService:
    # Patch MovieAnalyzer used inside AnalysisService to our fake
    monkeypatch.setattr(analysis_module, "MovieAnalyzer", FakeMovieAnalyzer)

    dp = FakeDataProcessor()
    service = AnalysisService(data_processor=dp)

    # attach dp so tests can inspect it
    service._fake_dp = dp
    # and fake analyzer
    assert isinstance(service._analyzer, FakeMovieAnalyzer)
    return service


# ---------- Tests ----------

def test_analysis_service_init_loads_and_validates(analysis_service: AnalysisService):
    dp: FakeDataProcessor = analysis_service._fake_dp  # type: ignore[attr-defined]

    # load_data for both files called
    assert "movies.csv" in dp.loaded_files
    assert "ratings.csv" in dp.loaded_files

    # validations executed
    assert dp.validated_movies is True
    assert dp.validated_ratings is True

    # movies_df and ratings_df are set
    assert isinstance(analysis_service.movies_df, pd.DataFrame)
    assert isinstance(analysis_service.ratings_df, pd.DataFrame)
    assert not analysis_service.movies_df.empty
    assert not analysis_service.ratings_df.empty


def test_get_movies_dataset_stats_uses_aggregate_statistics(analysis_service: AnalysisService):
    dp: FakeDataProcessor = analysis_service._fake_dp  # type: ignore[attr-defined]

    stats = analysis_service.get_movies_dataset_stats()

    assert stats["row_count"] == len(analysis_service.movies_df)
    assert dp.stats_called_with is analysis_service.movies_df


def test_get_top_movies_maps_to_dtos(analysis_service: AnalysisService):
    analyzer: FakeMovieAnalyzer = analysis_service._analyzer  # type: ignore[assignment]

    result = analysis_service.get_top_movies(limit=5, min_ratings=10)

    # Analyzer called with correct parameters
    assert analyzer.get_top_movies_called_with == (5, 10)

    # DTO mapping correct
    assert len(result) == 2
    first = result[0]
    assert first.movie_id == 1
    assert first.title == "Movie 1"
    assert first.genres == "Drama"
    assert first.avg_rating == 4.5
    assert first.rating_count == 100


def test_get_genre_trends_maps_to_dtos(analysis_service: AnalysisService):
    analyzer: FakeMovieAnalyzer = analysis_service._analyzer  # type: ignore[assignment]

    genres = analysis_service.get_genre_trends()

    assert analyzer.analyze_genre_trends_called is True
    assert len(genres) == 2
    assert genres[0].genre == "Drama"
    assert genres[0].avg_rating == 4.3
    assert genres[0].rating_count == 50


def test_get_user_statistics_maps_to_dto(analysis_service: AnalysisService):
    analyzer: FakeMovieAnalyzer = analysis_service._analyzer  # type: ignore[assignment]

    stats = analysis_service.get_user_statistics(user_id=42)

    assert analyzer.get_user_statistics_called_with == 42
    assert stats.user_id == 42
    assert stats.avg_rating == 4.1
    assert stats.rating_count == 5
    assert isinstance(stats.rating_distribution, dict)
    assert isinstance(stats.genre_preferences, list)
    assert isinstance(stats.genre_preferences, list)
    first_pref = stats.genre_preferences[0]
    assert isinstance(first_pref, dict)
    assert "genre" in first_pref
    assert first_pref["genre"] == "Drama"



def test_get_time_series_analysis_normalizes_and_maps(analysis_service: AnalysisService):
    analyzer: FakeMovieAnalyzer = analysis_service._analyzer  # type: ignore[assignment]

    ts_points = analysis_service.get_time_series_analysis()

    assert analyzer.time_series_called is True
    assert len(ts_points) == 2

    first = ts_points[0]
    # Types and normalization
    assert isinstance(first.date, date)
    assert isinstance(first.avg_rating, float)
    assert isinstance(first.rating_count, int)
    assert first.avg_rating == 4.25
    assert first.rating_count == 10
