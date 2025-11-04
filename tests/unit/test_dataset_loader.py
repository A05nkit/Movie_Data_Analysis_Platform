# tests/test_dataset_loader.py
from pathlib import Path

import pandas as pd
import pytest

from app.infrastructure.dataset_loader import DatasetLoader
from app.core.exceptions import DataLoadError
from app.config.settings import settings


def test_load_csv_success(tmp_path, monkeypatch):
    # Point data_folder to a temporary directory
    monkeypatch.setattr(settings, "data_folder", str(tmp_path))

    # Create a simple CSV file
    csv_path = tmp_path / "movies.csv"
    csv_path.write_text("movieId,title\n1,Toy Story\n", encoding="utf-8")

    loader = DatasetLoader()
    df = loader.load_csv("movies.csv")

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert list(df.columns) == ["movieId", "title"]
    assert df.loc[0, "title"] == "Toy Story"


def test_load_csv_file_not_found_raises_dataloaderror(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "data_folder", str(tmp_path))

    loader = DatasetLoader()

    with pytest.raises(DataLoadError) as excinfo:
        loader.load_csv("does_not_exist.csv")

    msg = str(excinfo.value)
    assert "Dataset file not found" in msg
    assert "does_not_exist.csv" in msg


def test_load_csv_unicode_decode_error_raises_dataloaderror(monkeypatch):
    loader = DatasetLoader()

    def fake_read_csv(*args, **kwargs):
        # encoding, object, start, end, reason
        raise UnicodeDecodeError("utf-8", b"\x80", 0, 1, "invalid start byte")

    monkeypatch.setattr(pd, "read_csv", fake_read_csv)

    # data_folder/path value doesn't matter here; read_csv is mocked
    with pytest.raises(DataLoadError) as excinfo:
        loader.load_csv("any.csv")

    msg = str(excinfo.value)
    assert "Failed to decode dataset" in msg


def test_load_csv_generic_exception_raises_dataloaderror(monkeypatch):
    loader = DatasetLoader()

    def fake_read_csv(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(pd, "read_csv", fake_read_csv)

    with pytest.raises(DataLoadError) as excinfo:
        loader.load_csv("any.csv")

    msg = str(excinfo.value)
    assert "Unexpected error while loading dataset" in msg
