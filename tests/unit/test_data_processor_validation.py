import pandas as pd
import pytest

from app.core.data_processor import DataProcessor
from app.core.exceptions import DataValidationError
from app.infrastructure.dataset_loader import DatasetLoader


class DummyLoader(DatasetLoader):
    """We won't call load_csv here, but DataProcessor requires a loader."""
    def load_csv(self, relative_path: str) -> pd.DataFrame:  # type: ignore[override]
        return pd.DataFrame()


@pytest.fixture
def processor() -> DataProcessor:
    return DataProcessor(dataset_loader=DummyLoader())


# ---------- clean_data / aggregate_statistics ----------

def test_clean_data_raises_on_empty_dataframe(processor: DataProcessor):
    df = pd.DataFrame()
    with pytest.raises(DataValidationError) as excinfo:
        processor.clean_data(df)

    assert "Input DataFrame is empty" in str(excinfo.value)


def test_aggregate_statistics_raises_on_empty_dataframe(processor: DataProcessor):
    df = pd.DataFrame()
    with pytest.raises(DataValidationError) as excinfo:
        processor.aggregate_statistics(df)

    assert "Cannot aggregate statistics on empty dataset" in str(excinfo.value)


def test_filter_data_raises_on_unknown_column(processor: DataProcessor):
    df = pd.DataFrame(
        {
            "year": [2000, 2001],
            "rating": [4.0, 3.5],
        }
    )

    with pytest.raises(DataValidationError) as excinfo:
        processor.filter_data(df, genre="Drama")

    msg = str(excinfo.value)
    assert "Unknown filter column" in msg
    assert "genre" in msg


# ---------- validate_movies ----------

def test_validate_movies_missing_required_columns_raises(processor: DataProcessor):
    # Missing 'genres' column
    movies_df = pd.DataFrame(
        {
            "movieId": [1],
            "title": ["A"],
        }
    )

    with pytest.raises(DataValidationError) as excinfo:
        processor.validate_movies(movies_df)

    msg = str(excinfo.value)
    assert "Movies dataset is missing required columns" in msg
    assert "genres" in str(excinfo.value.details.get("missing_columns", []))


def test_validate_movies_duplicate_movie_ids_raises(processor: DataProcessor):
    movies_df = pd.DataFrame(
        {
            "movieId": [1, 1],
            "title": ["A", "A-dup"],
            "genres": ["Drama", "Drama"],
        }
    )

    with pytest.raises(DataValidationError) as excinfo:
        processor.validate_movies(movies_df)

    msg = str(excinfo.value)
    assert "Duplicate movieId values found" in msg
    dup_sample = excinfo.value.details.get("duplicate_movie_ids_sample", [])
    assert 1 in dup_sample


# ---------- validate_ratings ----------

def test_validate_ratings_missing_required_columns_raises(processor: DataProcessor):
    # Missing 'timestamp'
    ratings_df = pd.DataFrame(
        {
            "userId": [10],
            "movieId": [1],
            "rating": [4.0],
        }
    )
    movies_df = pd.DataFrame({"movieId": [1], "title": ["A"], "genres": ["Drama"]})

    with pytest.raises(DataValidationError) as excinfo:
        processor.validate_ratings(ratings_df, movies_df)

    msg = str(excinfo.value)
    assert "Ratings dataset is missing required columns" in msg
    assert "timestamp" in str(excinfo.value.details.get("missing_columns", []))


def test_validate_ratings_invalid_rating_range_raises(processor: DataProcessor):
    ratings_df = pd.DataFrame(
        {
            "userId": [10, 11],
            "movieId": [1, 2],
            "rating": [4.0, 6.0],  # 6.0 is out of [0.5, 5.0]
            "timestamp": [111111, 222222],
        }
    )
    movies_df = pd.DataFrame(
        {
            "movieId": [1, 2],
            "title": ["A", "B"],
            "genres": ["Drama", "Comedy"],
        }
    )

    with pytest.raises(DataValidationError) as excinfo:
        processor.validate_ratings(ratings_df, movies_df)

    msg = str(excinfo.value)
    assert "Ratings out of allowed range" in msg
    invalid_sample = excinfo.value.details.get("invalid_ratings_sample", [])
    assert any(r["rating"] == 6.0 for r in invalid_sample)


def test_validate_ratings_unknown_movie_ids_raises(processor: DataProcessor):
    ratings_df = pd.DataFrame(
        {
            "userId": [10],
            "movieId": [99],  # not in movies_df
            "rating": [4.0],
            "timestamp": [111111],
        }
    )
    movies_df = pd.DataFrame(
        {
            "movieId": [1],
            "title": ["A"],
            "genres": ["Drama"],
        }
    )

    with pytest.raises(DataValidationError) as excinfo:
        processor.validate_ratings(ratings_df, movies_df)

    msg = str(excinfo.value)
    assert "Ratings referencing unknown movie IDs" in msg
    unknown_sample = excinfo.value.details.get("unknown_movie_ids_sample", [])
    assert 99 in unknown_sample
