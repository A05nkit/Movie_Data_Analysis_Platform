# app/core/recommender.py
from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

import pandas as pd

from app.core.exceptions import RecommendationError
from app.core.interfaces import ISimpleRecommender


class SimpleRecommender(ISimpleRecommender):
    """
    Very simple, explainable recommender:

    - get_similar_movies:
        * Use Jaccard similarity on genre sets to find movies similar to a given movie.
        * Only return movies with similarity > 0 (i.e., share at least one genre).
        * Rank by (similarity, avg_rating, rating_count).

    - get_user_recommendations:
        * Determine user's favourite genres based on movies rated >= 4.0.
        * Recommend unseen movies that share those genres.
        * Rank by (genre overlap, avg_rating, rating_count).
    """

    def __init__(self, movies_df: pd.DataFrame, ratings_df: pd.DataFrame) -> None:
        # Copy to avoid mutating external DataFrames
        self.movies_df = movies_df.copy()
        self.ratings_df = ratings_df.copy()

        # Normalize genres: "Action|Comedy" -> ["Action", "Comedy"]
        if "genres" in self.movies_df.columns:
            self.movies_df["genres_list"] = (
                self.movies_df["genres"].fillna("(no genres)").str.split("|")
            )
        else:
            self.movies_df["genres_list"] = [[] for _ in range(len(self.movies_df))]

        # Precompute movie-level rating statistics
        self._movie_stats = (
            self.ratings_df.groupby("movieId")["rating"]
            .agg(avg_rating="mean", rating_count="count")
            .reset_index()
        )

        # Convenience merged view (not strictly required, but handy)
        self._movie_data = self.movies_df.merge(
            self._movie_stats, on="movieId", how="left"
        )

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _ensure_movie_exists(self, movie_id: int) -> None:
        if movie_id not in self.movies_df["movieId"].values:
            raise RecommendationError(
                f"Movie ID {movie_id} not found",
                details={"movie_id": movie_id},
            )

    def _ensure_user_exists(self, user_id: int) -> None:
        if user_id not in self.ratings_df["userId"].values:
            raise RecommendationError(
                f"No ratings found for user {user_id}",
                details={"user_id": user_id},
            )

    @staticmethod
    def _jaccard(a: Set[str], b: Optional[List[str]]) -> float:
        """Jaccard similarity between two genre sets."""
        if not b:
            return 0.0
        bb = set(b)
        union = a | bb
        if not union:
            return 0.0
        return len(a & bb) / len(union)

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def get_similar_movies(self, movie_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Return a list of similar movies as dicts:
        {
            "movie_id": int,
            "title": str,
            "genres": str,
            "avg_rating": float,
            "rating_count": int,
        }
        """
        self._ensure_movie_exists(movie_id)

        # Get target movie's genres
        target_row = self.movies_df[self.movies_df["movieId"] == movie_id].iloc[0]
        target_genres = set(target_row["genres_list"])

        # Compute similarity for all movies
        movies_with_sim = self.movies_df.copy()
        movies_with_sim["similarity"] = movies_with_sim["genres_list"].apply(
            lambda g: self._jaccard(target_genres, g)
        )

        # Merge in rating stats
        merged = movies_with_sim.merge(self._movie_stats, on="movieId", how="left")

        # Filter out the target movie itself and zero-similarity movies
        ranked = (
            merged[
                (merged["movieId"] != movie_id)
                & (merged["similarity"] > 0)
            ]
            .sort_values(
                by=["similarity", "avg_rating", "rating_count"],
                ascending=[False, False, False],
            )
            .head(limit)
        )

        result: List[Dict[str, Any]] = [
            {
                "movie_id": int(row["movieId"]),
                "title": str(row["title"]),
                "genres": str(row["genres"]),
                "avg_rating": float(row["avg_rating"]),
                "rating_count": int(row["rating_count"]),
            }
            for _, row in ranked.iterrows()
            if not pd.isna(row["avg_rating"])
        ]

        if not result:
            raise RecommendationError(
                "No similar movies found",
                details={"movie_id": movie_id},
            )

        return result

    def get_user_recommendations(
        self, user_id: int, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Recommend unseen movies for a user based on their favourite genres
        (rated >= 4.0). Returns full movie dicts with rating stats.
        """
        self._ensure_user_exists(user_id)

        user_ratings = self.ratings_df[self.ratings_df["userId"] == user_id]

        # Movies user has already rated
        seen_movie_ids = set(user_ratings["movieId"].unique())

        # Favourite genres from movies rated >= 4.0
        liked = user_ratings[user_ratings["rating"] >= 4.0]
        liked_movie_ids = liked["movieId"].unique().tolist()

        if liked_movie_ids:
            liked_genres_list = self.movies_df[
                self.movies_df["movieId"].isin(liked_movie_ids)
            ]["genres_list"].tolist()
            favourite_genres: Set[str] = set(
                g for genres in liked_genres_list for g in genres
            )
        else:
            # If the user has no high ratings, fall back to an empty set (no genre preference)
            favourite_genres = set()

        # Candidates: movies the user has not yet seen
        unseen_movies = self.movies_df[
            ~self.movies_df["movieId"].isin(seen_movie_ids)
        ].copy()

        # If no favourite genres, we can just recommend top globally rated unseen movies
        if not favourite_genres:
            merged = unseen_movies.merge(
                self._movie_stats,
                on="movieId",
                how="left",
            )
            ranked = (
                merged.sort_values(
                    by=["avg_rating", "rating_count"],
                    ascending=[False, False],
                )
                .head(limit)
            )
        else:
            # Compute genre overlap as Jaccard vs favourite_genres
            unseen_movies["similarity"] = unseen_movies["genres_list"].apply(
                lambda g: self._jaccard(favourite_genres, g)
            )
            merged = unseen_movies.merge(
                self._movie_stats,
                on="movieId",
                how="left",
            )
            ranked = (
                merged[merged["similarity"] > 0]
                .sort_values(
                    by=["similarity", "avg_rating", "rating_count"],
                    ascending=[False, False, False],
                )
                .head(limit)
            )

        result: List[Dict[str, Any]] = [
            {
                "movie_id": int(row["movieId"]),
                "title": str(row["title"]),
                "genres": str(row["genres"]),
                "avg_rating": float(row["avg_rating"]),
                "rating_count": int(row["rating_count"]),
            }
            for _, row in ranked.iterrows()
            if not pd.isna(row["avg_rating"])
        ]

        if not result:
            # For this simple implementation, returning an empty list is acceptable,
            # but we keep a consistent error pattern.
            return []

        return result
