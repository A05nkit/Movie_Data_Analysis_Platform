# app/services/analysis_service.py
from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd

from app.core.data_processor import DataProcessor
from app.core.movie_analyzer import MovieAnalyzer
from app.models.dto import TopMovieDto, UserStatsDto, GenreTrendDto, TimeSeriesPointDto


class AnalysisService:
    """Application/service layer for analytics use cases."""

    def __init__(self, data_processor: DataProcessor) -> None:
        self._data_processor = data_processor

        # Load raw
        movies_raw = self._data_processor.load_data("movies.csv")
        ratings_raw = self._data_processor.load_data("ratings.csv")

        # Clean
        movies_df = self._data_processor.clean_data(movies_raw)
        ratings_df = self._data_processor.clean_data(ratings_raw)

        # Validate
        self._data_processor.validate_movies(movies_df)
        self._data_processor.validate_ratings(ratings_df, movies_df)

        self.movies_df = movies_df
        self.ratings_df = ratings_df

        self._analyzer = MovieAnalyzer(self.movies_df, self.ratings_df)

        # Simple in-memory cache for top movies by (limit, min_ratings)
        self._top_movies_cache: Dict[tuple[int, int], List[TopMovieDto]] = {}


    def get_movies_dataset_stats(self) -> Dict[str, Any]:
        return self._data_processor.aggregate_statistics(self.movies_df)

    def get_top_movies(self, limit: int, min_ratings: int) -> List[TopMovieDto]:
        movies = self._analyzer.get_top_movies(limit=limit, min_ratings=min_ratings)
        return [TopMovieDto(**m) for m in movies]

    def get_genre_trends(self) -> List[GenreTrendDto]:
        result = self._analyzer.analyze_genre_trends()
        genres = result["genres"]
        return [GenreTrendDto(**g) for g in genres]

    def get_user_statistics(self, user_id: int) -> UserStatsDto:
        stats = self._analyzer.get_user_statistics(user_id)
        return UserStatsDto(**stats)

    def get_time_series_analysis(self) -> List[TimeSeriesPointDto]:
        result = self._analyzer.generate_time_series_analysis()
        ts = result["time_series"]

        normalized = [
        {
            "date": p["date"],  # <-- this is a datetime.date
            "avg_rating": float(p["avg_rating"]),
            "rating_count": int(p["rating_count"]),
        }
        for p in ts
                    ]
        return [TimeSeriesPointDto(**p) for p in normalized]


