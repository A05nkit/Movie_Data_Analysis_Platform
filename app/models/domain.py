from __future__ import annotations
from dataclasses import dataclass
from typing import List


@dataclass
class Movie:
    movie_id: int
    title: str
    genres: str


@dataclass
class UserRating:
    user_id: int
    movie_id: int
    rating: float
    timestamp: int


@dataclass
class GenreStats:
    genre: str
    avg_rating: float
    rating_count: int


@dataclass
class TimeSeriesPoint:
    date: str
    avg_rating: float
    rating_count: int


@dataclass
class TopMovie:
    movie_id: int
    title: str
    genres: str
    avg_rating: float
    rating_count: int
