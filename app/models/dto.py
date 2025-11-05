from __future__ import annotations

from typing import Dict, List
from pydantic import BaseModel, Field
from datetime import date


class TopMovieDto(BaseModel):
    """
    Data Transfer Object (DTO) representing a single top-rated movie.

    Attributes:
        movie_id (int): Unique identifier for the movie.
        title (str): Movie title.
        genres (str): Comma-separated list of genres the movie belongs to.
        avg_rating (float): Average rating across all users for this movie.
        rating_count (int): Total number of ratings the movie has received.
    """
    movie_id: int
    title: str
    genres: str
    avg_rating: float
    rating_count: int


class UserStatsDto(BaseModel):
    """
    DTO representing aggregated statistics for a specific user's rating behavior.

    Attributes:
        user_id (int): Unique identifier for the user.
        avg_rating (float): Average rating given by the user.
        rating_count (int): Total number of ratings provided by the user.
        rating_distribution (Dict[float, int]): Mapping of rating values to their frequencies.
            For example: {5.0: 10, 4.0: 7, 3.0: 2}.
        genre_preferences (List[Dict]): List of dictionaries representing the user's
            preferred genres and their associated metrics (e.g., average rating, count).
    """
    user_id: int
    avg_rating: float
    rating_count: int
    rating_distribution: Dict[float, int]
    genre_preferences: List[Dict]


class GenreTrendDto(BaseModel):
    """
    DTO representing aggregated rating trends for a specific movie genre.

    Attributes:
        genre (str): Genre name.
        avg_rating (float): Average rating for movies in this genre.
        rating_count (int): Total number of ratings for all movies in this genre.
    """
    genre: str
    avg_rating: float
    rating_count: int


class TimeSeriesPointDto(BaseModel):
    """
    DTO representing a single data point in a time series of ratings.

    Attributes:
        date (date): The date associated with the data point.
        avg_rating (float): Average rating recorded on that date.
        rating_count (int): Total number of ratings recorded on that date.
    """
    date: date
    avg_rating: float
    rating_count: int


class TopMoviesQuery(BaseModel):
    """
    Query model for retrieving top-rated movies.

    Attributes:
        limit (int): Maximum number of movies to return.
            Must be greater than 0 and less than or equal to 100. Default is 10.
        min_ratings (int): Minimum number of ratings required for a movie to be included.
            Must be at least 1. Default is 50.
    """
    limit: int = Field(10, gt=0, le=100)
    min_ratings: int = Field(50, ge=1)


class RecommendationQuery(BaseModel):
    """
    Query model for generating personalized movie recommendations.

    Attributes:
        limit (int): Maximum number of recommendations to return.
            Must be greater than 0 and less than or equal to 100. Default is 10.
    """
    limit: int = Field(10, gt=0, le=100)
