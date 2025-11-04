# tests/test_recommender.py
import pandas as pd
import pytest

from app.core.recommender import SimpleRecommender
from app.core.exceptions import RecommendationError


@pytest.fixture
def movies_df() -> pd.DataFrame:
    # 4 movies with overlapping genres
    return pd.DataFrame(
        {
            "movieId": [1, 2, 3, 4],
            "title": ["M1", "M2", "M3", "M4"],
            "genres": ["Drama|Comedy", "Comedy", "Action", "Drama"],
        }
    )


@pytest.fixture
def ratings_df(movies_df) -> pd.DataFrame:
    # Ratings for 4 users to exercise all branches
    return pd.DataFrame(
        {
            "userId": [1, 1, 1, 2, 2, 3, 4, 4, 4, 4],
            "movieId": [1, 2, 3, 1, 4, 1, 1, 2, 3, 4],
            "rating": [4.5, 3.0, 5.0, 4.0, 2.0, 3.0, 4.0, 4.0, 4.0, 4.0],
            "timestamp": [1] * 10,
        }
    )
    # User 1: likes 1 & 3 (>=4) → has favourite genres + unseen movie 4
    # User 2: one >=4 rating (movie 1) → favourite genres exist, unseen {2,3}
    # User 3: only <4 rating → no favourite genres → fallback branch
    # User 4: has rated all movies → no unseen movies → returns []


@pytest.fixture
def recommender(movies_df, ratings_df) -> SimpleRecommender:
    return SimpleRecommender(movies_df, ratings_df)


# ---------- Helper methods & _jaccard ----------

def test_ensure_movie_exists_raises_on_unknown_movie(movies_df, ratings_df):
    rec = SimpleRecommender(movies_df, ratings_df)
    with pytest.raises(RecommendationError) as excinfo:
        rec.get_similar_movies(movie_id=999, limit=5)

    msg = str(excinfo.value)
    assert "Movie ID 999 not found" in msg
    assert excinfo.value.details.get("movie_id") == 999


def test_ensure_user_exists_raises_on_unknown_user(recommender: SimpleRecommender):
    with pytest.raises(RecommendationError) as excinfo:
        recommender.get_user_recommendations(user_id=999, limit=5)

    msg = str(excinfo.value)
    assert "No ratings found for user 999" in msg
    assert excinfo.value.details.get("user_id") == 999


def test_jaccard_edge_cases():
    # Empty target set
    a = set()
    assert SimpleRecommender._jaccard(a, None) == 0.0
    assert SimpleRecommender._jaccard(a, []) == 0.0

    # Non-empty sets with overlap
    a = {"Drama", "Comedy"}
    b = ["Drama", "Action"]
    j = SimpleRecommender._jaccard(a, b)
    # |intersection| = 1, |union| = 3 -> 1/3
    assert pytest.approx(j, rel=1e-6) == 1.0 / 3.0


# ---------- get_similar_movies ----------

def test_get_similar_movies_happy_path(recommender: SimpleRecommender):
    # Movie 1 shares "Comedy" with movie 2 and genres with movie 4 (Drama)
    result = recommender.get_similar_movies(movie_id=1, limit=3)

    assert isinstance(result, list)
    assert len(result) >= 1
    first = result[0]
    assert "movie_id" in first
    assert "title" in first
    assert "genres" in first
    assert "avg_rating" in first
    assert "rating_count" in first
    # Should never include the target movie itself
    assert all(r["movie_id"] != 1 for r in result)


def test_get_similar_movies_raises_when_no_similar_found(movies_df, ratings_df):
    # Make genres all unique so Jaccard is always 0 -> no similar movies
    movies_unique = movies_df.copy()
    movies_unique["genres"] = ["Drama", "Comedy", "Action", "Sci-Fi"]

    rec = SimpleRecommender(movies_unique, ratings_df)

    with pytest.raises(RecommendationError) as excinfo:
        rec.get_similar_movies(movie_id=1, limit=5)

    msg = str(excinfo.value)
    assert "No similar movies found" in msg
    assert excinfo.value.details.get("movie_id") == 1


# ---------- get_user_recommendations ----------

def test_get_user_recommendations_with_favourite_genres(recommender: SimpleRecommender):
    # User 1: liked movies 1 and 3 (>=4) with genres Drama/Comedy/Action
    recs = recommender.get_user_recommendations(user_id=1, limit=10)

    assert isinstance(recs, list)
    # User 1 has seen movies 1,2,3 → unseen movie 4 should be recommended if stats exist
    # result may or may not include more than one movie depending on stats,
    # but at least 0 or 1 is okay; just ensure all are unseen
    seen_ids = {1, 2, 3}
    for r in recs:
        assert r["movie_id"] not in seen_ids


def test_get_user_recommendations_fallback_when_no_favourite_genres(recommender: SimpleRecommender):
    # User 3: only rating <4 → no favourite genres -> fallback branch
    recs = recommender.get_user_recommendations(user_id=3, limit=10)

    # Recommendations may be non-empty; check they are unseen for user 3
    seen_ids = {1}
    for r in recs:
        assert r["movie_id"] not in seen_ids


def test_get_user_recommendations_returns_empty_when_no_unseen(recommender: SimpleRecommender):
    # User 4 has rated all movies -> no unseen_movies, so result becomes [] and is returned
    recs = recommender.get_user_recommendations(user_id=4, limit=10)

    assert recs == []
