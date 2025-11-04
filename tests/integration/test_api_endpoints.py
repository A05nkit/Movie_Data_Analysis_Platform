import pandas as pd

from app.core.recommender import SimpleRecommender


def _sample_movies_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "movieId": [1, 2, 3],
            "title": ["Action One", "Comedy One", "Action Two"],
            "genres": ["Action", "Comedy", "Action"],
        }
    )


def _sample_ratings_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "userId": [1, 1, 2, 3],
            "movieId": [1, 2, 3, 2],
            "rating": [5.0, 3.0, 4.0, 4.5],
            "timestamp": [1, 1, 1, 1],
        }
    )


def test_get_similar_movies_returns_same_genre():
    """
    For movie 1 ("Action One", genre Action), the similar movies
    should include movie 3 (also Action) and exclude movie 2 (Comedy).
    """
    movies_df = _sample_movies_df()
    ratings_df = _sample_ratings_df()
    recommender = SimpleRecommender(movies_df, ratings_df)

    similar = recommender.get_similar_movies(movie_id=1, limit=5)

    # We expect a list of movie objects (dicts)
    assert isinstance(similar, list)
    assert all(isinstance(m, dict) for m in similar)

    # Extract movie_ids from returned objects
    similar_ids = {m["movie_id"] for m in similar}

    # Movie 1 is "Action", Movie 3 is also "Action"
    assert 3 in similar_ids
    # Movie 2 is "Comedy" only; with genre-based similarity it should not be suggested
    assert 2 not in similar_ids


def test_get_user_recommendations_excludes_seen_movies():
    """
    User 1 has rated movies 1 and 2 already; recommendations
    should not include those movieIds.
    """
    movies_df = _sample_movies_df()
    ratings_df = _sample_ratings_df()
    recommender = SimpleRecommender(movies_df, ratings_df)

    recs = recommender.get_user_recommendations(user_id=1, limit=5)

    # We expect a list of movie objects (dicts)
    assert isinstance(recs, list)
    assert all(isinstance(m, dict) for m in recs)

    rec_ids = {m["movie_id"] for m in recs}

    # User 1 has already seen movies 1 and 2
    assert 1 not in rec_ids
    assert 2 not in rec_ids
