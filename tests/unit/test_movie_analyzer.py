# tests/test_movie_analyzer.py
from datetime import date

import pandas as pd
import pytest

from app.core.movie_analyzer import MovieAnalyzer
from app.core.exceptions import DataValidationError, AnalysisError


@pytest.fixture
def sample_movies_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "movieId": [1, 2, 3],
            "title": ["Movie 1", "Movie 2", "Movie 3"],
            "genres": ["Drama|Comedy", "Comedy", "Action"],
        }
    )


@pytest.fixture
def sample_ratings_df() -> pd.DataFrame:
    # Two different dates in timestamps for time-series test
    return pd.DataFrame(
        {
            "userId": [10, 10, 11, 12],
            "movieId": [1, 2, 1, 3],
            "rating": [4.0, 5.0, 3.0, 2.5],
            "timestamp": [
                1609459200,  # 2021-01-01
                1609459200,  # 2021-01-01
                1609545600,  # 2021-01-02
                1609545600,  # 2021-01-02
            ],
        }
    )


@pytest.fixture
def analyzer(sample_movies_df, sample_ratings_df) -> MovieAnalyzer:
    return MovieAnalyzer(sample_movies_df, sample_ratings_df)


# ---------- __init__ ----------

def test_movie_analyzer_init_raises_on_empty_data(sample_movies_df):
    ratings_empty = pd.DataFrame(columns=["userId", "movieId", "rating", "timestamp"])
    with pytest.raises(DataValidationError) as excinfo:
        MovieAnalyzer(sample_movies_df, ratings_empty)

    assert "Movies or ratings data is empty" in str(excinfo.value)


# ---------- get_top_movies ----------

def test_get_top_movies_happy_path(analyzer: MovieAnalyzer):
    result = analyzer.get_top_movies(limit=2, min_ratings=1)

    assert isinstance(result, list)
    assert len(result) <= 2
    first = result[0]
    assert "movie_id" in first
    assert "title" in first
    assert "genres" in first
    assert "avg_rating" in first
    assert "rating_count" in first


def test_get_top_movies_raises_when_no_movies_meet_min_ratings(analyzer: MovieAnalyzer):
    # Set min_ratings higher than any movie's rating_count
    with pytest.raises(AnalysisError) as excinfo:
        analyzer.get_top_movies(limit=5, min_ratings=999)

    msg = str(excinfo.value)
    assert "No movies found with the specified minimum number of ratings" in msg
    assert excinfo.value.details.get("min_ratings") == 999


# ---------- analyze_genre_trends ----------

def test_analyze_genre_trends_returns_genre_stats(analyzer: MovieAnalyzer):
    result = analyzer.analyze_genre_trends()

    assert "genres" in result
    genres = result["genres"]
    assert isinstance(genres, list)
    assert len(genres) > 0
    first = genres[0]
    assert "genre" in first
    assert "avg_rating" in first
    assert "rating_count" in first


# ---------- get_user_statistics ----------

def test_get_user_statistics_happy_path(analyzer: MovieAnalyzer):
    stats = analyzer.get_user_statistics(user_id=10)

    assert stats["user_id"] == 10
    assert isinstance(stats["avg_rating"], float)
    assert isinstance(stats["rating_count"], int)
    assert isinstance(stats["genre_preferences"], list)
    assert isinstance(stats["rating_distribution"], dict)
    # rating_distribution keys are rating values as strings or floats
    assert len(stats["rating_distribution"]) >= 1


def test_get_user_statistics_raises_for_user_with_no_ratings(analyzer: MovieAnalyzer):
    with pytest.raises(AnalysisError) as excinfo:
        analyzer.get_user_statistics(user_id=999)

    msg = str(excinfo.value)
    assert "No ratings found for user 999" in msg
    assert excinfo.value.details.get("user_id") == 999


# ---------- generate_time_series_analysis ----------

def test_generate_time_series_analysis_groups_by_date(analyzer: MovieAnalyzer):
    result = analyzer.generate_time_series_analysis()

    assert "time_series" in result
    ts = result["time_series"]
    assert isinstance(ts, list)
    assert len(ts) >= 2  # we have two dates in sample_ratings_df

    first = ts[0]
    assert "date" in first
    assert "avg_rating" in first
    assert "rating_count" in first
    # date should be serializable (date object becomes string later in DTO)
    assert isinstance(first["date"], date)
