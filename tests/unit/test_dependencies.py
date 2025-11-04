# tests/test_dependencies.py
from app.api import dependencies
from app.infrastructure.dataset_loader import DatasetLoader
from app.core.data_processor import DataProcessor
from app.services.analysis_service import AnalysisService
from app.services.recommendation_service import RecommendationService


def test_get_dataset_loader_cached_singleton():
    loader1 = dependencies.get_dataset_loader()
    loader2 = dependencies.get_dataset_loader()
    assert isinstance(loader1, DatasetLoader)
    assert loader1 is loader2  # cached singleton


def test_get_data_processor_returns_singleton():
    dependencies.get_dataset_loader.cache_clear()
    dependencies.get_data_processor.cache_clear()

    dp1 = dependencies.get_data_processor()
    dp2 = dependencies.get_data_processor()

    assert isinstance(dp1, DataProcessor)
    assert dp1 is dp2  # cached singleton


def test_get_analysis_service_returns_singleton():
    dependencies.get_dataset_loader.cache_clear()
    dependencies.get_data_processor.cache_clear()
    dependencies.get_analysis_service.cache_clear()

    svc1 = dependencies.get_analysis_service()
    svc2 = dependencies.get_analysis_service()

    assert isinstance(svc1, AnalysisService)
    assert svc1 is svc2


def test_get_recommendation_service_returns_singleton():
    dependencies.get_dataset_loader.cache_clear()
    dependencies.get_data_processor.cache_clear()
    dependencies.get_recommendation_service.cache_clear()

    svc1 = dependencies.get_recommendation_service()
    svc2 = dependencies.get_recommendation_service()

    assert isinstance(svc1, RecommendationService)
    assert svc1 is svc2
