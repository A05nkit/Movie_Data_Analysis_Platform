from datetime import date

from app.api.routers.analytics import (
    get_genre_trends,
    get_time_series,
    generate_report,
)
import app.api.routers.analytics as analytics_module


# ---------- Fakes ----------

class FakeAnalysisService:
    def __init__(self):
        self._analyzer = object()  # just needs to exist for generate_report
        self.genre_trends_called = False
        self.time_series_called = False

    def get_genre_trends(self):
        self.genre_trends_called = True
        # Shape doesn't matter for direct function call (response_model is FastAPI-only)
        return [
            {"genre": "Drama", "avg_rating": 4.3, "rating_count": 50},
            {"genre": "Comedy", "avg_rating": 4.0, "rating_count": 30},
        ]

    def get_time_series_analysis(self):
        self.time_series_called = True
        return [
            {"date": date(2020, 1, 1), "avg_rating": 4.2, "rating_count": 10},
            {"date": date(2020, 1, 2), "avg_rating": 3.8, "rating_count": 5},
        ]


class FakeDataVisualizer:
    def __init__(self):
        self.created = True


class FakeReportService:
    def __init__(self, analyzer, visualizer):
        self.analyzer = analyzer
        self.visualizer = visualizer
        self.generate_called = False

    def generate_dashboard(self) -> str:
        self.generate_called = True
        return "fake_dashboard.html"


# ---------- Tests ----------

def test_get_genre_trends_uses_analysis_service():
    service = FakeAnalysisService()

    result = get_genre_trends(service=service)

    assert service.genre_trends_called is True
    assert isinstance(result, list)
    assert result[0]["genre"] == "Drama"


def test_get_time_series_uses_analysis_service():
    service = FakeAnalysisService()

    result = get_time_series(service=service)

    assert service.time_series_called is True
    assert isinstance(result, list)
    assert "date" in result[0]
    assert "avg_rating" in result[0]
    assert "rating_count" in result[0]


def test_generate_report_creates_report_with_report_service(monkeypatch):
    service = FakeAnalysisService()

    # Patch DataVisualizer and ReportService used inside analytics router
    monkeypatch.setattr(analytics_module, "DataVisualizer", FakeDataVisualizer)
    monkeypatch.setattr(analytics_module, "ReportService", FakeReportService)

    response = generate_report(service=service)

    # Response is a dict with the report path
    assert response["report_path"] == "fake_dashboard.html"
