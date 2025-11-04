# tests/test_main_exceptions.py
import asyncio

from starlette.requests import Request

from app.main import app
from app.core.exceptions import (
    AppError,
    DataLoadError,
    DataValidationError,
    AnalysisError,
    RecommendationError,
    VisualizationError,
)


def _make_request() -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/test",
        "headers": [],
    }
    return Request(scope)


def test_data_validation_error_handler():
    handler = app.exception_handlers[DataValidationError]
    request = _make_request()
    exc = DataValidationError("invalid data", details={"field": "rating"})

    response = asyncio.run(handler(request, exc))

    assert response.status_code == 422
    body = response.body.decode("utf-8")
    assert "data_validation_error" in body
    assert "invalid data" in body
    assert "rating" in body


def test_data_load_error_handler():
    handler = app.exception_handlers[DataLoadError]
    request = _make_request()
    exc = DataLoadError("load failed", details={"path": "movies.csv"})

    response = asyncio.run(handler(request, exc))

    assert response.status_code == 400
    body = response.body.decode("utf-8")
    assert "DataLoadError" in body
    assert "load failed" in body
    assert "movies.csv" in body


def test_analysis_error_handler():
    handler = app.exception_handlers[AnalysisError]
    request = _make_request()
    exc = AnalysisError("analysis failed", details={"step": "trend"})

    response = asyncio.run(handler(request, exc))

    assert response.status_code == 400
    body = response.body.decode("utf-8")
    assert "AnalysisError" in body
    assert "analysis failed" in body
    assert "trend" in body


def test_recommendation_error_handler():
    handler = app.exception_handlers[RecommendationError]
    request = _make_request()
    exc = RecommendationError("recommendation failed", details={"user_id": 1})

    response = asyncio.run(handler(request, exc))

    assert response.status_code == 400
    body = response.body.decode("utf-8")
    assert "RecommendationError" in body
    assert "recommendation failed" in body
    assert "user_id" in body


def test_visualization_error_handler():
    handler = app.exception_handlers[VisualizationError]
    request = _make_request()
    exc = VisualizationError("viz failed", details={"plot": "rating_dist"})

    response = asyncio.run(handler(request, exc))

    assert response.status_code == 400
    body = response.body.decode("utf-8")
    assert "VisualizationError" in body
    assert "viz failed" in body
    assert "rating_dist" in body


def test_generic_app_error_handler():
    handler = app.exception_handlers[AppError]
    request = _make_request()
    exc = AppError("something bad", details={"info": "debug"})

    response = asyncio.run(handler(request, exc))

    assert response.status_code == 500
    body = response.body.decode("utf-8")
    assert "internal_application_error" in body
    assert "An internal error occurred" in body
