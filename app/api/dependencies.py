from __future__ import annotations
from functools import lru_cache
from app.core.data_processor import DataProcessor
from app.infrastructure.dataset_loader import DatasetLoader
from app.services.analysis_service import AnalysisService
from app.services.recommendation_service import RecommendationService


@lru_cache
def get_dataset_loader() -> DatasetLoader:
    """
    Singleton DatasetLoader.

    NOTE: We do NOT pass any arguments here, because DatasetLoader.__init__
    currently takes no parameters in your implementation.
    """
    return DatasetLoader()


@lru_cache
def get_data_processor() -> DataProcessor:
    """Singleton DataProcessor using the shared DatasetLoader."""
    loader = get_dataset_loader()
    return DataProcessor(dataset_loader=loader)


@lru_cache
def get_analysis_service() -> AnalysisService:
    """
    Singleton AnalysisService.

    Loads + cleans + validates datasets once at startup and keeps them in memory
    for all analytics endpoints.
    """
    data_processor = get_data_processor()
    return AnalysisService(data_processor=data_processor)


@lru_cache
def get_recommendation_service() -> RecommendationService:
    """
    Singleton RecommendationService.

    Uses the same DataProcessor / CSV source, but constructs its own SimpleRecommender.
    """
    data_processor = get_data_processor()
    return RecommendationService(data_processor=data_processor)
