from __future__ import annotations

from typing import Any, Dict, Set

import pandas as pd

from app.core.exceptions import DataValidationError
from app.core.interfaces import IDataProcessor
from app.infrastructure.dataset_loader import DatasetLoader


class DataProcessor(IDataProcessor):
    """Concrete implementation of IDataProcessor."""

    MOVIES_REQUIRED_COLUMNS: Set[str] = {"movieId", "title", "genres"}
    RATINGS_REQUIRED_COLUMNS: Set[str] = {"userId", "movieId", "rating", "timestamp"}

    def __init__(self, dataset_loader: DatasetLoader) -> None:
        self._loader = dataset_loader

    # ---------- Core IDataProcessor methods ----------

    def load_data(self, file_path: str) -> pd.DataFrame:
        return self._loader.load_csv(file_path)

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            raise DataValidationError("Input DataFrame is empty")

        df = df.drop_duplicates().reset_index(drop=True)
        return df

    def aggregate_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty:
            raise DataValidationError("Cannot aggregate statistics on empty dataset")

        stats: Dict[str, Any] = {
            "row_count": int(len(df)),
            "column_count": int(df.shape[1]),
        }

        numeric_df = df.select_dtypes(include="number")
        if not numeric_df.empty:
            stats["numeric_summary"] = numeric_df.describe().to_dict()

        return stats

    def filter_data(self, df: pd.DataFrame, **filters: Any) -> pd.DataFrame:
        filtered = df
        for column, value in filters.items():
            if column not in filtered.columns:
                raise DataValidationError(
                    f"Unknown filter column: {column}",
                    details={"column": column},
                )
            filtered = filtered[filtered[column] == value]
        return filtered

    # ---------- Data quality validation helpers ----------

    def validate_movies(self, movies_df: pd.DataFrame) -> None:
        """Validate movies dataset schema and basic integrity."""
        missing = self.MOVIES_REQUIRED_COLUMNS - set(movies_df.columns)
        if missing:
            raise DataValidationError(
                "Movies dataset is missing required columns",
                details={"missing_columns": sorted(missing)},
            )

        # movieId should be unique
        if movies_df["movieId"].duplicated().any():
            dup_ids = (
                movies_df[movies_df["movieId"].duplicated()]["movieId"]
                .unique()
                .tolist()
            )
            raise DataValidationError(
                "Duplicate movieId values found in movies dataset",
                details={"duplicate_movie_ids_sample": dup_ids[:10]},
            )

    def validate_ratings(self, ratings_df: pd.DataFrame, movies_df: pd.DataFrame) -> None:
        """Validate ratings dataset schema, value ranges, and referential integrity."""
        missing = self.RATINGS_REQUIRED_COLUMNS - set(ratings_df.columns)
        if missing:
            raise DataValidationError(
                "Ratings dataset is missing required columns",
                details={"missing_columns": sorted(missing)},
            )

        # Rating value range check
        if not ratings_df["rating"].between(0.5, 5.0).all():
            invalid = ratings_df[~ratings_df["rating"].between(0.5, 5.0)]
            raise DataValidationError(
                "Ratings out of allowed range [0.5, 5.0]",
                details={"invalid_ratings_sample": invalid.head(10).to_dict(orient="records")},
            )

        # Referential integrity: every rated movieId must exist in movies_df
        unknown_movie_ids = set(ratings_df["movieId"].unique()) - set(
            movies_df["movieId"].unique()
        )
        if unknown_movie_ids:
            raise DataValidationError(
                "Ratings referencing unknown movie IDs",
                details={
                    "unknown_movie_ids_sample": sorted(list(unknown_movie_ids))[:10],
                    "unknown_movie_ids_count": len(unknown_movie_ids),
                },
            )
