from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routers import movies as movies_router
from app.api.routers import users as users_router
from app.api.routers import analytics as analytics_router
from app.config.settings import settings
from app.core.exceptions import (
    AppError,
    DataLoadError,
    DataValidationError,
    AnalysisError,
    RecommendationError,
    VisualizationError,
)
from app.infrastructure.logging_config import configure_logging


def create_app() -> FastAPI:
    configure_logging()
    logger = logging.getLogger(__name__)

    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
    )

    # ---------- Root endpoint ----------
    @app.get("/", tags=["meta"])
    async def root():
        return {
            "status": "ok",
            "app": settings.app_name,
            "version": "1.0.0",
            "docs_url": "/docs",
            "health": "healthy",
        }
    # ---------- Exception handlers ----------

    @app.exception_handler(DataValidationError)
    async def handle_data_validation(request: Request, exc: DataValidationError):
        logger.warning(
            "DataValidationError at %s %s: %s details=%s",
            request.method,
            request.url.path,
            str(exc),
            exc.details,
        )
        return JSONResponse(
            status_code=422,
            content={
                "error": "data_validation_error",
                "message": str(exc),
                "details": exc.details,
            },
        )

    @app.exception_handler(DataLoadError)
    async def handle_data_load_error(request: Request, exc: DataLoadError):
        logger.error(
            "DataLoadError at %s %s: %s details=%s",
            request.method,
            request.url.path,
            str(exc),
            exc.details,
        )
        return JSONResponse(
            status_code=400,
            content={
                "error": "DataLoadError",
                "message": str(exc),
                "details": exc.details,
            },
        )

    @app.exception_handler(AnalysisError)
    async def handle_analysis_error(request: Request, exc: AnalysisError):
        logger.error(
            "AnalysisError at %s %s: %s details=%s",
            request.method,
            request.url.path,
            str(exc),
            exc.details,
        )
        return JSONResponse(
            status_code=400,
            content={
                "error": "AnalysisError",
                "message": str(exc),
                "details": exc.details,
            },
        )

    @app.exception_handler(RecommendationError)
    async def handle_recommendation_error(request: Request, exc: RecommendationError):
        logger.error(
            "RecommendationError at %s %s: %s details=%s",
            request.method,
            request.url.path,
            str(exc),
            exc.details,
        )
        return JSONResponse(
            status_code=400,
            content={
                "error": "RecommendationError",
                "message": str(exc),
                "details": exc.details,
            },
        )

    @app.exception_handler(VisualizationError)
    async def handle_visualization_error(request: Request, exc: VisualizationError):
        logger.error(
            "VisualizationError at %s %s: %s details=%s",
            request.method,
            request.url.path,
            str(exc),
            exc.details,
        )
        return JSONResponse(
            status_code=400,
            content={
                "error": "VisualizationError",
                "message": str(exc),
                "details": exc.details,
            },
        )

    # Generic catch-all for any other AppError not specifically handled above
    @app.exception_handler(AppError)
    async def handle_generic_app_error(request: Request, exc: AppError):
        logger.error(
            "Unhandled AppError at %s %s: %s details=%s",
            request.method,
            request.url.path,
            str(exc),
            exc.details,
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_application_error",
                "message": "An internal error occurred. Please try again later.",
            },
        )

    # ---------- Routers ----------

    app.include_router(movies_router.router, prefix="/movies", tags=["movies"])
    app.include_router(users_router.router, prefix="/users", tags=["users"])
    app.include_router(analytics_router.router, prefix="/analytics", tags=["analytics"])

    return app


app = create_app()
