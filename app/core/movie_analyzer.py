from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd

from app.core.exceptions import AnalysisError, DataValidationError
from app.core.interfaces import IMovieAnalyzer


class MovieAnalyzer(IMovieAnalyzer):
    """Performing analytics based on movies + ratings DataFrames."""

    def __init__(self, movies_df: pd.DataFrame, ratings_df: pd.DataFrame) -> None:
        if movies_df.empty or ratings_df.empty:
            raise DataValidationError("Movies or ratings data is empty")

        self.movies_df = movies_df.copy()
        self.ratings_df = ratings_df.copy()

        # Normalize genres: "Action|Comedy" -> list
        self.movies_df["genres_list"] = self.movies_df["genres"].fillna("(no genres)").str.split("|")

    def _movie_stats(self) -> pd.DataFrame:
        grouped = (
            self.ratings_df
            .groupby("movieId")["rating"]
            .agg(
                avg_rating="mean",
                rating_count="count",
            )
            .reset_index()
        )
        merged = grouped.merge(self.movies_df, on="movieId", how="left")
        return merged

    def get_top_movies(self, limit: int = 10, min_ratings: int = 50) -> List[Dict[str, Any]]:
        stats_df = self._movie_stats()
        filtered = stats_df[stats_df["rating_count"] >= min_ratings]
        if filtered.empty:
            raise AnalysisError(
                "No movies found with the specified minimum number of ratings",
                details={"min_ratings": min_ratings},
            )

        top_df = filtered.sort_values(
            by=["avg_rating", "rating_count"],
            ascending=[False, False],
        ).head(limit)

        result: List[Dict[str, Any]] = []
        for _, row in top_df.iterrows():
            result.append(
                {
                    "movie_id": int(row["movieId"]),
                    "title": str(row["title"]),
                    "genres": str(row["genres"]),
                    "avg_rating": float(row["avg_rating"]),
                    "rating_count": int(row["rating_count"]),
                }
            )
        return result

    def analyze_genre_trends(self) -> Dict[str, Any]:
        # explode genres
        movies_exploded = self.movies_df.explode("genres_list")
        ratings_with_movies = self.ratings_df.merge(
            movies_exploded[["movieId", "genres_list"]],
            on="movieId",
            how="left",
        )

        by_genre = (
            ratings_with_movies
            .groupby("genres_list")["rating"]
            .agg(
                avg_rating="mean",
                rating_count="count",
            )
            .reset_index()
            .rename(columns={"genres_list": "genre"})
        )

        by_genre = by_genre[by_genre["genre"].notna()]

        return {
            "genres": by_genre.to_dict(orient="records"),
        }

    def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        user_ratings = self.ratings_df[self.ratings_df["userId"] == user_id]
        if user_ratings.empty:
            raise AnalysisError(
                f"No ratings found for user {user_id}",
                details={"user_id": user_id},
            )

        avg_rating = float(user_ratings["rating"].mean())
        rating_count = int(user_ratings.shape[0])

        # Merging with movies to get genres
        merged = user_ratings.merge(self.movies_df[["movieId", "genres_list"]], on="movieId", how="left")
        exploded = merged.explode("genres_list")
        genre_stats = (
            exploded.groupby("genres_list")["rating"]
            .agg(
                avg_rating="mean",
                rating_count="count",
            )
            .reset_index()
            .rename(columns={"genres_list": "genre"})
        )

        rating_distribution = (
            user_ratings["rating"].value_counts().sort_index().to_dict()
        )

        return {
            "user_id": user_id,
            "avg_rating": avg_rating,
            "rating_count": rating_count,
            "genre_preferences": genre_stats.to_dict(orient="records"),
            "rating_distribution": rating_distribution,
        }

    def generate_time_series_analysis(self) -> Dict[str, Any]:
        df = self.ratings_df.copy()        
        df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")
        df["date"] = df["datetime"].dt.date

        by_date = (
            df.groupby("date")["rating"]
            .agg(
                avg_rating="mean",
                rating_count="count",
            )
            .reset_index()
        )

        return {
            "time_series": by_date.to_dict(orient="records"),
        }
