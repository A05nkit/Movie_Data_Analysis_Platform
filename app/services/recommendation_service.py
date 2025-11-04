from __future__ import annotations

from typing import List

from app.core.data_processor import DataProcessor
from app.core.recommender import SimpleRecommender
from app.models.dto import TopMovieDto


class RecommendationService:
    """Application/service layer for recommendation use cases."""

    def __init__(self, data_processor: DataProcessor) -> None:
        self._data_processor = data_processor

        # Load + clean datasets
        movies_raw = self._data_processor.load_data("movies.csv")
        ratings_raw = self._data_processor.load_data("ratings.csv")

        movies_df = self._data_processor.clean_data(movies_raw)
        ratings_df = self._data_processor.clean_data(ratings_raw)

        self._recommender = SimpleRecommender(movies_df, ratings_df)

    def get_similar_movies(self, movie_id: int, limit: int) -> List[TopMovieDto]:
        movies = self._recommender.get_similar_movies(movie_id=movie_id, limit=limit)
        return [TopMovieDto(**m) for m in movies]

    def get_user_recommendations(self, user_id: int, limit: int) -> List[TopMovieDto]:
        movies = self._recommender.get_user_recommendations(user_id=user_id, limit=limit)
        return [TopMovieDto(**m) for m in movies]
