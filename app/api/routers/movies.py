from __future__ import annotations
from typing import List
from fastapi import APIRouter, Depends, Path, Query
from app.api.dependencies import get_analysis_service, get_recommendation_service
from app.models.dto import TopMovieDto, TopMoviesQuery
from app.services.analysis_service import AnalysisService
from app.services.recommendation_service import RecommendationService

router = APIRouter()


@router.get("/stats", response_model=dict)
def get_movies_stats(service: AnalysisService = Depends(get_analysis_service)):
    return service.get_movies_dataset_stats()


@router.get("/top", response_model=List[TopMovieDto])
def get_top_movies(
    query: TopMoviesQuery = Depends(),
    service: AnalysisService = Depends(get_analysis_service),
):
    return service.get_top_movies(limit=query.limit, min_ratings=query.min_ratings)


@router.get("/{movie_id}/similar", response_model=List[TopMovieDto])
def get_similar_movies(
    movie_id: int = Path(..., gt=0),
    limit: int = Query(10, gt=0, le=50),
    service: RecommendationService = Depends(get_recommendation_service),
):
    return service.get_similar_movies(movie_id=movie_id, limit=limit)
