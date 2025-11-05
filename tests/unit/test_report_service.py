from pathlib import Path

import pandas as pd

from app.services.report_service import ReportService


class FakeAnalyzer:
    def __init__(self):
        # Simple ratings_df, shape doesn't matter for this test
        self.ratings_df = pd.DataFrame(
            {
                "userId": [1, 2],
                "movieId": [10, 20],
                "rating": [4.0, 5.0],
            }
        )
        self.analyze_genre_trends_called = False

    def analyze_genre_trends(self):
        self.analyze_genre_trends_called = True
        # This must be convertible to DataFrame via pd.DataFrame(...["genres"])
        return {
            "genres": [
                {"genre": "Drama", "rating_count": 100},
                {"genre": "Comedy", "rating_count": 50},
            ]
        }


class FakeVisualizer:
    def __init__(self):
        self.rating_df_received = None
        self.genre_df_received = None
        self.analysis_results_received = None

    def create_rating_distribution(self, df):
        # Just capture the DataFrame for assertions
        self.rating_df_received = df
        return "rating_dist_plot.png"

    def plot_genre_popularity(self, df):
        self.genre_df_received = df
        return "genre_popularity_plot.png"

    def generate_dashboard_report(self, analysis_results):
        self.analysis_results_received = analysis_results
        # Simulate returning a path to the dashboard
        return "dashboard.html"


def test_generate_dashboard_happy_path():
    analyzer = FakeAnalyzer()
    visualizer = FakeVisualizer()

    service = ReportService(analyzer=analyzer, visualizer=visualizer)

    result_path = service.generate_dashboard()

    # Check return value
    assert result_path == "dashboard.html"

    # Analyzer was used
    assert analyzer.analyze_genre_trends_called is True

    # Visualizer got the correct dataframes
    assert visualizer.rating_df_received is analyzer.ratings_df
    assert isinstance(visualizer.genre_df_received, type(analyzer.ratings_df))
    assert set(visualizer.genre_df_received.columns) == {"genre", "rating_count"}

    # Analysis results passed correctly to dashboard report
    assert visualizer.analysis_results_received == {
        "rating_distribution_plot": "rating_dist_plot.png",
        "genre_popularity_plot": "genre_popularity_plot.png",
    }
