import pytest
import pandas as pd

from app.core.data_processor import DataProcessor
from app.core.exceptions import DataValidationError
from app.infrastructure.dataset_loader import DatasetLoader


class DummyLoader(DatasetLoader):
    """Overrides load_csv to avoid touching the real file system in unit tests."""

    def __init__(self, df: pd.DataFrame):
        self._df = df

    def load_csv(self, relative_path: str) -> pd.DataFrame:  # type: ignore[override]
        return self._df.copy()


def test_aggregate_statistics_basic():
    # existing test ...
    df = pd.DataFrame({"movieId": [1, 2, 3], "value": [10.0, 20.0, 30.0]})
    loader = DummyLoader(df)
    processor = DataProcessor(dataset_loader=loader)

    loaded = processor.load_data("whatever.csv")
    cleaned = processor.clean_data(loaded)
    stats = processor.aggregate_statistics(cleaned)

    assert stats["row_count"] == 3
    assert stats["column_count"] == 2
    assert "numeric_summary" in stats
    assert stats["numeric_summary"]["value"]["mean"] == 20.0


def test_validate_movies_missing_column_raises():
    df = pd.DataFrame(
        {
            "movieId": [1],
            "title": ["X"],  # 'genres' missing
        }
    )
    loader = DummyLoader(df)
    processor = DataProcessor(dataset_loader=loader)

    with pytest.raises(DataValidationError) as exc_info:
        processor.validate_movies(df)

    assert "missing required columns" in str(exc_info.value)


def test_validate_ratings_out_of_range_rating_raises():
    movies = pd.DataFrame(
        {"movieId": [1], "title": ["X"], "genres": ["Action"]}
    )
    ratings = pd.DataFrame(
        {
            "userId": [1],
            "movieId": [1],
            "rating": [10.0],  # invalid
            "timestamp": [1],
        }
    )
    loader = DummyLoader(ratings)
    processor = DataProcessor(dataset_loader=loader)

    with pytest.raises(DataValidationError) as exc_info:
        processor.validate_ratings(ratings, movies)

    assert "Ratings out of allowed range" in str(exc_info.value)
    
    
def test_validate_ratings_unknown_movie_id_raises():
    movies = pd.DataFrame(
        {"movieId": [1], "title": ["X"], "genres": ["Action"]}
    )
    ratings = pd.DataFrame(
        {
            "userId": [1],
            "movieId": [999],  # not in movies
            "rating": [4.0],
            "timestamp": [1],
        }
    )
    loader = DummyLoader(ratings)
    processor = DataProcessor(dataset_loader=loader)

    with pytest.raises(DataValidationError) as exc_info:
        processor.validate_ratings(ratings, movies)

    assert "unknown movie IDs" in str(exc_info.value)
