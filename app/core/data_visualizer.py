from __future__ import annotations

import os
import uuid
from typing import Dict, Any

import matplotlib.pyplot as plt
import pandas as pd

from app.config.settings import settings
from app.core.exceptions import VisualizationError
from app.core.interfaces import IDataVisualizer


class DataVisualizer(IDataVisualizer):
    """Generates plots and HTML dashboard."""

    def __init__(self) -> None:
        os.makedirs(settings.reports_folder, exist_ok=True)

    def _save_plot(self, name: str) -> str:
        """
        Saving the current matplotlib figure under a unique filename derived
        from `name` to avoid different requests clobbering each other's images.
        """
        base, ext = os.path.splitext(name)
        unique_name = f"{base}_{uuid.uuid4().hex}{ext}"
        path = os.path.join(settings.reports_folder, unique_name)
        try:
            plt.tight_layout()
            plt.savefig(path)
            plt.close()
        except Exception as exc:
            raise VisualizationError(
                f"Failed to save plot: {path}",
                details={"path": path},
            ) from exc
        return path

    def create_rating_distribution(self, df: pd.DataFrame) -> str:
        if df.empty:
            raise VisualizationError("Cannot create rating distribution for empty DataFrame")

        plt.figure()
        df["rating"].hist(bins=10)
        plt.xlabel("Rating")
        plt.ylabel("Count")
        plt.title("Rating Distribution")

     
        return self._save_plot("rating_distribution.png")

    def plot_genre_popularity(self, df: pd.DataFrame) -> str:
        if df.empty:
            raise VisualizationError("Cannot create genre popularity chart for empty DataFrame")

        plt.figure()
        top = df.sort_values("rating_count", ascending=False).head(20)
        plt.bar(top["genre"], top["rating_count"])
        plt.xticks(rotation=90)
        plt.xlabel("Genre")
        plt.ylabel("Number of Ratings")
        plt.title("Genre Popularity (by rating count)")

        return self._save_plot("genre_popularity.png")

    def generate_dashboard_report(self, analysis_results: Dict[str, Any] ) -> str:
        """
        Very simple HTML dashboard that references generated plots.

        Using a unique HTML filename per report to avoid concurrent
        requests overwriting each other's dashboards.
        """
        report_filename = f"dashboard_{uuid.uuid4().hex}.html"
        report_path = os.path.join(settings.reports_folder, report_filename)

        rating_dist_path = analysis_results.get("rating_distribution_plot", "")
        genre_plot_path = analysis_results.get("genre_popularity_plot", "")

        html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Movie Analytics Dashboard</title>
</head>
<body>
  <h1>Movie Analytics Dashboard</h1>

  <h2>Rating Distribution</h2>
  <img src="{os.path.basename(rating_dist_path)}" alt="Rating Distribution" />

  <h2>Genre Popularity</h2>
  <img src="{os.path.basename(genre_plot_path)}" alt="Genre Popularity" />
</body>
</html>
"""

        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(html)
        except Exception as exc:
            raise VisualizationError(
                "Failed to write dashboard HTML",
                details={"path": report_path},
            ) from exc

        return report_path
