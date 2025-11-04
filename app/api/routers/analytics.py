from __future__ import annotations
"""
Analytics API router.

Provides endpoints for movie analytics:

- GET /genre-trends: returns genre trend data
- GET /time-series: returns time-series data
- GET /report: generates a dashboard report

Uses:
- AnalysisService for computing analytics
- DataVisualizer for creating visuals
- ReportService to assemble and save reports

Response DTOs:
- GenreTrendDto
- TimeSeriesPointDto
"""
from typing import List
from fastapi import APIRouter, Depends
from app.api.dependencies import get_analysis_service
from app.core.data_visualizer import DataVisualizer
from app.services.analysis_service import AnalysisService
from app.services.report_service import ReportService
from app.models.dto import GenreTrendDto, TimeSeriesPointDto

router = APIRouter()


@router.get("/genre-trends", response_model=List[GenreTrendDto])
def get_genre_trends(service: AnalysisService = Depends(get_analysis_service)):
    return service.get_genre_trends()


@router.get("/time-series", response_model=List[TimeSeriesPointDto])
def get_time_series(service: AnalysisService = Depends(get_analysis_service)):
    return service.get_time_series_analysis()


@router.get("/report", response_model=dict)
def generate_report(service: AnalysisService = Depends(get_analysis_service)):
    visualizer = DataVisualizer()
    report_service = ReportService(analyzer=service._analyzer, visualizer=visualizer)
    path = report_service.generate_dashboard()
    return {"report_path": path}