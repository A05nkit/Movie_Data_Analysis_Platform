# app/infrastructure/cache.py
from __future__ import annotations

from functools import lru_cache
from typing import Callable, TypeVar

T = TypeVar("T")


def singleton(factory: Callable[[], T]) -> Callable[[], T]:
    """Turn a factory into a process-wide singleton provider."""
    cached = lru_cache(maxsize=1)(factory)
    return cached
