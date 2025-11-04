# tests/test_interfaces.py
from typing import Any, Dict, List

import pandas as pd
import pytest

from app.core.interfaces import (
    IDataProcessor,
    IMovieAnalyzer,
    IDataVisualizer,
    ISimpleRecommender,
)


# ---------- Dummy implementations to exercise abstract methods ----------

class DummyDataProcessor(IDataProcessor):
    def load_data(self, file_path: str) -> pd.DataFrame:
        return super().load_data(file_path)

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        return super().clean_data(df)

    def aggregate_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        return super().aggregate_statistics(df)

    def filter_data(self, df: pd.DataFrame, **filters: Any) -> pd.DataFrame:
        return super().filter_data(df, **filters)


class DummyMovieAnalyzer(IMovieAnalyzer):
    def get_top_movies(self, limit: int = 10, min_ratings: int = 50) -> List[Dict[str, Any]]:
        return super().get_top_movies(limit=limit, min_ratings=min_ratings)

    def analyze_genre_trends(self) -> Dict[str, Any]:
        return super().analyze_genre_trends()

    def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        return super().get_user_statistics(user_id)

    def generate_time_series_analysis(self) -> Dict[str, Any]:
        return super().generate_time_series_analysis()


class DummyDataVisualizer(IDataVisualizer):
    def create_rating_distribution(self, df: pd.DataFrame) -> str:
        return super().create_rating_distribution(df)

    def plot_genre_popularity(self, df: pd.DataFrame) -> str:
        return super().plot_genre_popularity(df)

    def generate_dashboard_report(self, analysis_results: Dict[str, Any]) -> str:
        return super().generate_dashboard_report(analysis_results)


class DummySimpleRecommender(ISimpleRecommender):
    def get_similar_movies(self, movie_id: int, limit: int = 10) -> List[int]:
        return super().get_similar_movies(movie_id=movie_id, limit=limit)

    def get_user_recommendations(self, user_id: int, limit: int = 10) -> List[int]:
        return super().get_user_recommendations(user_id=user_id, limit=limit)


# ---------- Tests ----------

def test_idata_processor_abstract_methods_raise_not_implemented():
    d = DummyDataProcessor()

    with pytest.raises(NotImplementedError):
        d.load_data("movies.csv")

    df = pd.DataFrame()
    with pytest.raises(NotImplementedError):
        d.clean_data(df)

    with pytest.raises(NotImplementedError):
        d.aggregate_statistics(df)

    with pytest.raises(NotImplementedError):
        d.filter_data(df, year=2020)


def test_imovie_analyzer_abstract_methods_raise_not_implemented():
    d = DummyMovieAnalyzer()

    with pytest.raises(NotImplementedError):
        d.get_top_movies(limit=5, min_ratings=10)

    with pytest.raises(NotImplementedError):
        d.analyze_genre_trends()

    with pytest.raises(NotImplementedError):
        d.get_user_statistics(user_id=42)

    with pytest.raises(NotImplementedError):
        d.generate_time_series_analysis()


def test_idata_visualizer_abstract_methods_raise_not_implemented():
    d = DummyDataVisualizer()
    df = pd.DataFrame()

    with pytest.raises(NotImplementedError):
        d.create_rating_distribution(df)

    with pytest.raises(NotImplementedError):
        d.plot_genre_popularity(df)

    with pytest.raises(NotImplementedError):
        d.generate_dashboard_report({"dummy": True})


def test_isimple_recommender_abstract_methods_raise_not_implemented():
    d = DummySimpleRecommender()

    with pytest.raises(NotImplementedError):
        d.get_similar_movies(movie_id=1, limit=3)

    with pytest.raises(NotImplementedError):
        d.get_user_recommendations(user_id=99, limit=5)
