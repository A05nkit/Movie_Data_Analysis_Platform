from __future__ import annotations

from typing import Any, Dict, Optional


class AppError(Exception):
    """Base class for all domain/application errors."""

    def __init__(self, message: str, *, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.details = details or {}


class DataLoadError(AppError):
    """Problems loading raw data (missing file, unreadable format, etc.)."""


class DataValidationError(AppError):
    """Data integrity issues (missing columns, wrong types, inconsistent joins)."""


class AnalysisError(AppError):
    """Errors during statistical/analytical computations."""


class RecommendationError(AppError):
    """Errors in recommender logic (unknown user/movie, etc.)."""


class VisualizationError(AppError):
    """Chart/report generation issues."""
