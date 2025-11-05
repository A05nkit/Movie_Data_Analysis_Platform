from __future__ import annotations

from typing import Dict, Any

from app.core.data_visualizer import DataVisualizer
from app.core.movie_analyzer import MovieAnalyzer


class ReportService:
    """Generates HTML dashboard report."""

    def __init__(self, analyzer: MovieAnalyzer, visualizer: DataVisualizer) -> None:
        self._analyzer = analyzer
        self._visualizer = visualizer

    def generate_dashboard(self) -> str:
        # Rating distribution uses ratings_df
        rating_dist_plot = self._visualizer.create_rating_distribution(self._analyzer.ratings_df)

        # Genre popularity uses genre trends
        genre_trends = self._analyzer.analyze_genre_trends()
        genre_df = self._analyzer.ratings_df  # not perfect, but we can enhance later

        # Better: reconstruct a small df from genre_trends["genres"]
        import pandas as pd  # local import

        genre_df = pd.DataFrame(genre_trends["genres"])

        genre_popularity_plot = self._visualizer.plot_genre_popularity(genre_df)

        analysis_results: Dict[str, Any] = {
            "rating_distribution_plot": rating_dist_plot,
            "genre_popularity_plot": genre_popularity_plot,
        }

        return self._visualizer.generate_dashboard_report(analysis_results)
