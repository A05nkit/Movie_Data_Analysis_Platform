# 🎬 Movie Analytics Platform

A Python-based movie data analysis and recommendation platform built on the MovieLens dataset. Demonstrates advanced analytics, a clean layered architecture, and modern Python practices.

## Table of Contents

- Key features
- Architecture
- Data processing & analysis
- API endpoints
- Setup & running
- Testing & quality
- Error handling & logging
- Performance considerations
- Recommendations
- AI assistance usage

---

## Key Features

- Robust data processing: efficient loading and cleaning of MovieLens CSVs
- Statistical analysis: per-movie and per-genre metrics with significance thresholds
- Genre analytics: trend and popularity analysis
- User insights: per-user behavior and preferences
- Smart recommendations: content-based recommender (explainable)
- Visual analytics: interactive HTML dashboard and charts
- Quality assurance: unit and integration tests

---

## Core Architecture

Root layout:

```text
movie-analytics/
├─ app/
│  ├─ api/               # FastAPI endpoints and DI
│  ├─ core/              # Domain logic and analytics
│  ├─ services/          # Business orchestration layer
│  ├─ models/            # Domain entities and DTOs
│  ├─ config/            # Settings (pydantic BaseSettings)
│  ├─ infrastructure/    # Dataset loader, logging, cache
│  └─ main.py            # FastAPI app, exception mapping
├─ tests/                # Unit + integration tests
├─ data/                 # MovieLens CSVs
├─ reports/              # Generated HTML + plots
└─ README.md
```

Layers and responsibilities:

- API layer (app/api)

  - FastAPI routers: movies.py, users.py, analytics.py
  - DI via dependencies.py (simple singleton factories)
  - Pydantic DTOs for validation

- Service layer (app/services)

  - AnalysisService: orchestrates DataProcessor + MovieAnalyzer
  - RecommendationService: wraps SimpleRecommender
  - ReportService: builds dashboard using analyzer + visualizer

- Core / Domain (app/core)

  - DataProcessor: load, clean, filter, and basic stats
  - MovieAnalyzer: top movies, genre trends, user stats, time series, summary
  - DataVisualizer: charts and HTML report generation
  - SimpleRecommender: content-based recommendations
  - interfaces.py, exceptions.py: abstractions and domain errors

- Infrastructure (app/infrastructure)

  - DatasetLoader: CSV I/O
  - logging_config.py: centralized logging
  - cache.py: small singleton helpers

- Models (app/models)

  - domain.py: domain entities (Movie, UserRating, ...)
  - dto.py: Pydantic DTOs for API boundaries

  ### 2.3 Architecture Decisions & Trade-offs

- **Layered design instead of a monolith script**  
  Rather than writing a single notebook or script, the project is split into `api`, `services`, `core`, `infrastructure`, and `models`. This mirrors clean architecture and makes it easy to test and evolve individual pieces (e.g., swapping out the recommender).

- **Interfaces and dependency injection**  
  Even though Python doesn’t have C#-style interfaces, I modelled contracts using `abc.ABC` and injected concrete implementations in `api/dependencies.py`. This decouples web, orchestration, and core logic and makes unit testing straightforward.

- **In-memory analytics instead of a database**  
  For this assessment, everything runs in-memory using pandas. For larger datasets, I would consider:

  - Persisted pre-aggregations (e.g., in a columnar store),
  - Loading data in chunks,
  - Or streaming new ratings into a separate storage layer.

- **Simple content-based recommender**  
  The `SimpleRecommender` is intentionally straightforward (genre overlap + rating quality). It is explainable and easy to extend, without introducing heavyweight dependencies or model training pipelines for this assignment.

- **HTML report over notebook-only output**  
  In addition to code and APIs, a static HTML dashboard is generated so that non-technical stakeholders could consume the key charts and summaries without running notebooks.

---

## 3. Data Processing & Analysis

Datasets (expected under data/):

- data/movies.csv — movieId, title, genres
- data/ratings.csv — userId, movieId, rating, timestamp

DataProcessor responsibilities:

- Load CSVs via DatasetLoader
- Clean duplicates and validate rows
- Provide dataset stats (row_count, column_count, numeric summary)
- Support generic filtering by column

MovieAnalyzer responsibilities:

- Per-movie metrics: avg_rating, rating_count
- Top movies: filter by min_ratings, sort by avg_rating then rating_count
- Genre trends: explode multi-genre rows, compute avg_rating & rating_count per genre
- User statistics: per-user avg rating, counts, rating distribution, genre preferences
- Time series: date conversion and daily aggregates (rating_count, avg_rating)
- Dataset summary: descriptive stats and derived aggregates

### 3.3 Key Insights from the MovieLens Dataset

After running the analysis endpoints on the MovieLens data, a few patterns emerge:

- **Ratings distribution**  
  Most ratings cluster in the positive range (around 3.0–4.5), with relatively few very low scores. This suggests users are generally positively biased when they choose to rate a movie at all.

- **Movie popularity vs. quality**  
  Highly rated movies do not always have many ratings, and vice versa. The correlation between average rating and rating count (computed in `/analytics/summary`) is weak-to-moderate, which motivated the use of a **minimum rating count threshold** when ranking top movies.

- **Genre dynamics**  
  Genres like `<fill from /analytics/genre-trends>` tend to have the highest rating counts, whereas niche genres have fewer ratings but sometimes higher average scores. This distinction is captured in the `avg_rating` and `rating_count` metrics returned by `/analytics/genre-trends`.

- **User behavior**  
  A small fraction of very active users contribute a large number of ratings, while most users have relatively few. This long-tail pattern is visible in the user activity distribution in `/analytics/summary`.

---

## 4. API Endpoints

All endpoints expose OpenAPI docs at /docs.

Movies

- GET /movies/stats — basic movies dataset stats
- GET /movies/top?limit={limit}&min_ratings={min_ratings} — top movies (title, genres, avg_rating, rating_count)
- GET /movies/{movie_id}/similar?limit={limit} — similar movie IDs (genre overlap + rating quality)

Users

- GET /users/{user_id}/stats — per-user stats: avg rating, count, distribution, genre prefs
- GET /users/{user_id}/recommendations?limit={limit} — recommended movie IDs for user

Analytics

- GET /analytics/genre-trends — avg_rating and rating_count per genre
- GET /analytics/time-series — daily points: date, avg_rating, rating_count
- GET /analytics/summary — dataset-level summary and percentiles
- GET /analytics/report — generates reports/dashboard.html and returns its path

## 4.1 Example API Usage

Assuming the server is running at `http://127.0.0.1:8000`:

**Top movies**

````bash
curl "http://127.0.0.1:8000/movies/top?limit=10&min_ratings=50"

#  User statistics
curl "http://127.0.0.1:8000/users/1/stats"

# User recommendations
curl "http://127.0.0.1:8000/users/1/recommendations?limit=10"

#Genre trends
curl "http://127.0.0.1:8000/analytics/genre-trends"

#Dataset summary
curl "http://127.0.0.1:8000/analytics/summary"

#Generate HTML report
curl "http://127.0.0.1:8000/analytics/report"
# -> returns {"report_path": "reports/dashboard.html"}

---

## 5. Setup & Running

Requirements

- Python 3.9+ (tested through 3.13)
- pip, virtualenv

Installation (example Windows PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
````

Place MovieLens CSVs into data/:

- data/movies.csv
- data/ratings.csv

Run API

```bash
uvicorn app.main:app --reload
```

Open Swagger UI: http://127.0.0.1:8000/docs

---

## 6. Testing & Quality

Test layout:

- tests/unit/
  - test_data_processor.py
  - test_movie_analyzer.py
  - test_recommender.py
- tests/integration/
  - test_api_endpoints.py

Run tests:

```bash
pytest
```

Notes: core components are unit-tested with in-memory fakes; integration tests use FastAPI TestClient.

---

## 7. Error Handling & Logging

Domain errors (app/core/exceptions.py):

- AppError base class
- DataLoadError, DataValidationError, AnalysisError, RecommendationError, VisualizationError

FastAPI maps domain errors to HTTP responses:

- 422 — validation issues
- 400 — domain parameter errors (missing/invalid)
- 500 — unexpected AppError cases

Logging configured in app/infrastructure/logging_config.py and used in exception handlers.

---

## 8. Performance Considerations

- Data loaded and cleaned once at service startup and reused
- MovieAnalyzer precomputes and caches aggregates to avoid repeated groupby operations
- Numeric dtype tightening (float32, int32) where appropriate
- In-memory caches:
  - \_movie_stats_cache, \_genre_trends_cache, \_time_series_cache, \_dataset_summary_cache
- AnalysisService caches TopMovieDto lists by (limit, min_ratings)

### 8. Performance Optimizations

Although the MovieLens dataset fits comfortably in memory, a few optimizations were applied:

- **Single-pass loading and cleaning**  
  The datasets are loaded and cleaned once at application startup (`AnalysisService.__init__`), then reused across requests. This avoids repeated disk IO and reduces latency for API calls.

- **Pandas group-by and vectorized operations**  
  All analytics are implemented with `groupby`, `agg`, `merge`, and vectorized operations rather than Python loops. This leverages pandas’ C-optimized internals for speed.

- **Precomputed aggregates with in-memory caching**  
  `MovieAnalyzer` caches expensive computations like:

  - Per-movie stats (`avg_rating`, `rating_count`),
  - Genre trends,
  - Time-series aggregates,
  - Dataset summary statistics.  
    These are reused across requests without recomputation unless the underlying data changes.

- **Dtype narrowing**  
  The ratings dataframe narrows numeric columns to smaller dtypes where appropriate (`float32`, `int32`). This reduces memory footprint and can improve cache efficiency for large data.

If this were a production system on much larger datasets, I would consider:

- Using categorical dtypes for `userId`, `movieId`, and `genres`,
- Adding indices on frequently joined columns,
- Chunked loading or an analytical database (e.g., DuckDB, BigQuery).

---

## 9. Recommendations (Simple, Explainable)

SimpleRecommender:

- Similar movies: Jaccard similarity on genre sets, ranked by similarity, avg rating, rating count
- User recommendations: derive favourite genres from ratings >= 4.0, recommend unseen movies matching those genres ranked by avg rating and rating count

Designed to be replaceable with more advanced models (matrix factorization, embeddings, etc.).

---

## 10. AI Assistance Usage
