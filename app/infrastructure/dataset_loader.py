# app/infrastructure/dataset_loader.py
from __future__ import annotations

import os

import pandas as pd

from app.config.settings import settings
from app.core.exceptions import DataLoadError


class DatasetLoader:

    
    """Low-level CSV access (keeps file system concerns out of core)."""

    def load_csv(self, relative_path: str) -> pd.DataFrame:
        full_path = os.path.join(settings.data_folder, relative_path)

        try:
            df = pd.read_csv(full_path)
        except FileNotFoundError as exc:
            raise DataLoadError(
                f"Dataset file not found: {full_path}",
                details={"path": full_path},
            ) from exc
        except UnicodeDecodeError as exc:
            raise DataLoadError(
                f"Failed to decode dataset: {full_path}",
                details={"path": full_path},
            ) from exc
        except Exception as exc:
            raise DataLoadError(
                f"Unexpected error while loading dataset: {full_path}",
                details={"path": full_path},
            ) from exc

        return df
