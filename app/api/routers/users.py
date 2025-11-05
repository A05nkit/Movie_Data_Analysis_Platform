from __future__ import annotations
from typing import List
from fastapi import APIRouter, Depends, Path

from app.api.dependencies import (
    get_analysis_service,
    get_recommendation_service,
)
from app.models.dto import UserStatsDto, RecommendationQuery, TopMovieDto
from app.services.analysis_service import AnalysisService
from app.services.recommendation_service import RecommendationService

router = APIRouter()

@router.get("/{user_id}/stats", response_model=UserStatsDto)
def get_user_stats(
    user_id: int = Path(..., gt=0),
    service: AnalysisService = Depends(get_analysis_service),
):
    return service.get_user_statistics(user_id)


@router.get(
    "/{user_id}/recommendations",
    response_model=List[TopMovieDto],
)
def get_user_recommendations(
    user_id: int = Path(..., gt=0),
    query: RecommendationQuery = Depends(),
    service: RecommendationService = Depends(get_recommendation_service),
):
    return service.get_user_recommendations(user_id=user_id, limit=query.limit)

