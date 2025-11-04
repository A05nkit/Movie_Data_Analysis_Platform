# tests/test_data_visualizer.py
from pathlib import Path
import builtins

import matplotlib
matplotlib.use("Agg")  # safe non-GUI backend for tests

import matplotlib.pyplot as plt
import pandas as pd
import pytest

from app.core.data_visualizer import DataVisualizer
from app.core.exceptions import VisualizationError
from app.config.settings import settings


def test_create_rating_distribution_happy_path(tmp_path, monkeypatch):
    # Use temp reports folder
    monkeypatch.setattr(settings, "reports_folder", str(tmp_path))

    viz = DataVisualizer()  # covers __init__ + os.makedirs

    df = pd.DataFrame({"rating": [3.0, 4.0, 5.0]})

    path_str = viz.create_rating_distribution(df)
    path = Path(path_str)

    assert path.exists()
    assert path.name == "rating_distribution.png"


def test_create_rating_distribution_empty_df_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "reports_folder", str(tmp_path))
    viz = DataVisualizer()

    df = pd.DataFrame({"rating": []})

    with pytest.raises(VisualizationError) as excinfo:
        viz.create_rating_distribution(df)

    assert "empty DataFrame" in str(excinfo.value)


def test_plot_genre_popularity_happy_path(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "reports_folder", str(tmp_path))
    viz = DataVisualizer()

    df = pd.DataFrame(
        {
            "genre": ["Drama", "Comedy", "Action"],
            "rating_count": [100, 50, 20],
        }
    )

    path_str = viz.plot_genre_popularity(df)
    path = Path(path_str)

    assert path.exists()
    assert path.name == "genre_popularity.png"


def test_plot_genre_popularity_empty_df_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "reports_folder", str(tmp_path))
    viz = DataVisualizer()

    df = pd.DataFrame(columns=["genre", "rating_count"])

    with pytest.raises(VisualizationError) as excinfo:
        viz.plot_genre_popularity(df)

    assert "empty DataFrame" in str(excinfo.value)


def test_save_plot_error_raises_visualization_error(tmp_path, monkeypatch):
    """
    Exercise the exception branch in _save_plot by forcing plt.savefig to fail.
    """
    monkeypatch.setattr(settings, "reports_folder", str(tmp_path))
    viz = DataVisualizer()

    def fake_savefig(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(plt, "savefig", fake_savefig)

    with pytest.raises(VisualizationError) as excinfo:
        viz._save_plot("test_plot.png")

    assert "Failed to save plot" in str(excinfo.value)


def test_generate_dashboard_report_success(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "reports_folder", str(tmp_path))
    viz = DataVisualizer()

    analysis_results = {
        "rating_distribution_plot": str(tmp_path / "rating_distribution.png"),
        "genre_popularity_plot": str(tmp_path / "genre_popularity.png"),
    }

    report_path_str = viz.generate_dashboard_report(analysis_results)
    report_path = Path(report_path_str)

    assert report_path.exists()

    html = report_path.read_text(encoding="utf-8")
    # Only basenames are used in HTML
    assert "rating_distribution.png" in html
    assert "genre_popularity.png" in html
    assert "<title>Movie Analytics Dashboard</title>" in html


def test_generate_dashboard_report_write_error(tmp_path, monkeypatch):
    """
    Exercise the exception branch when writing the HTML file fails.
    """
    monkeypatch.setattr(settings, "reports_folder", str(tmp_path))
    viz = DataVisualizer()

    analysis_results = {
        "rating_distribution_plot": "rating_distribution.png",
        "genre_popularity_plot": "genre_popularity.png",
    }

    real_open = builtins.open

    def fake_open(*args, **kwargs):
        # Make only this specific write fail, leave other opens intact
        if str(args[0]).endswith("dashboard.html") and "w" in args[1]:
            raise OSError("disk full")
        return real_open(*args, **kwargs)

    monkeypatch.setattr(builtins, "open", fake_open)

    with pytest.raises(VisualizationError) as excinfo:
        viz.generate_dashboard_report(analysis_results)

    assert "Failed to write dashboard HTML" in str(excinfo.value)
