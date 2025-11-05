from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List

import pandas as pd


class IDataProcessor(ABC):
    @abstractmethod
    def load_data(self, file_path: str) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def aggregate_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def filter_data(self, df: pd.DataFrame, **filters: Any) -> pd.DataFrame:
        raise NotImplementedError


class IMovieAnalyzer(ABC):
    @abstractmethod
    def get_top_movies(self, limit: int = 10, min_ratings: int = 50) -> List[Dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def analyze_genre_trends(self) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def generate_time_series_analysis(self) -> Dict[str, Any]:
        raise NotImplementedError


class IDataVisualizer(ABC):
    @abstractmethod
    def create_rating_distribution(self, df: pd.DataFrame) -> str:
        raise NotImplementedError

    @abstractmethod
    def plot_genre_popularity(self, df: pd.DataFrame) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate_dashboard_report(self, analysis_results: Dict[str, Any]) -> str:
        raise NotImplementedError


class ISimpleRecommender(ABC):
    @abstractmethod
    def get_similar_movies(self, movie_id: int, limit: int = 10) -> List[int]:
        raise NotImplementedError

    @abstractmethod
    def get_user_recommendations(self, user_id: int, limit: int = 10) -> List[int]:
        raise NotImplementedError
