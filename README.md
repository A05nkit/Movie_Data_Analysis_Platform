# 🎬 Movie Data Analysis Platform

A FastAPI-powered service that loads MovieLens-style CSV files, cleans and validates them with pandas, and exposes movie analytics, personalized insights, and recommendation endpoints. The project emphasises a layered architecture, thorough validation, and reproducible visual reports.

## Features

- **Data ingestion & hygiene** – Load CSV assets from the configurable `data/` directory, drop duplicates, and enforce schema integrity for the movies and ratings datasets before any computation runs.【F:app/core/data_processor.py†L12-L110】【F:app/infrastructure/dataset_loader.py†L11-L37】
- **Exploratory analytics** – Produce dataset summaries, top-movie leaderboards, genre trends, user statistics, and time-series metrics through the `MovieAnalyzer` service layer.【F:app/services/analysis_service.py†L12-L64】【F:app/core/movie_analyzer.py†L11-L142】
- **Explainable recommendations** – Generate similar-movie suggestions and user-tailored picks via a genre-overlap recommender that honours validation and referential integrity checks.【F:app/services/recommendation_service.py†L10-L37】【F:app/core/recommender.py†L11-L173】
- **Automated reporting** – Build PNG visualisations and an HTML dashboard with collision-resistant filenames so concurrent requests never overwrite prior output.【F:app/core/data_visualizer.py†L15-L107】【F:app/services/report_service.py†L10-L33】
- **Robust API surface** – FastAPI routers expose analytics, movies, and user endpoints, while the application maps domain exceptions to clear HTTP responses.【F:app/api/routers/movies.py†L12-L31】【F:app/api/routers/users.py†L15-L32】【F:app/api/routers/analytics.py†L31-L46】【F:app/main.py†L23-L159】
- **Confidence via tests** – Unit and integration suites cover the API contract, core analytics, and recommender behaviour using FastAPI’s TestClient and in-memory dataframes.【F:tests/test_main.py†L1-L15】【F:tests/integration/test_api_endpoints.py†L1-L70】

## Project Structure

```
Movie_Data_Analysis_Platform/
├─ app/
│  ├─ api/                # FastAPI routers and dependency wiring
│  ├─ services/           # Application orchestration layer
│  ├─ core/               # Data processing, analytics, recommender, visuals
│  ├─ models/             # Pydantic DTOs
│  ├─ config/             # Environment-aware settings
│  ├─ infrastructure/     # CSV loader, logging helpers
│  └─ main.py             # FastAPI app factory + exception mapping
├─ data/                  # MovieLens CSV inputs (movies.csv, ratings.csv, ...)
├─ reports/               # Generated PNG charts and HTML dashboards
├─ tests/                 # Unit and integration coverage
└─ requirements.txt       # Runtime and tooling dependencies
```

## Getting Started

### 1. Prerequisites

- Python 3.9 or newer
- `pip` for dependency management

### 2. Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Data Paths (optional)

All paths default to the bundled `data/` and `reports/` folders, and can be overridden with environment variables prefixed by `MOVIE_APP_` (e.g., `MOVIE_APP_DATA_FOLDER=/path/to/csvs`).【F:app/config/settings.py†L6-L21】

### 4. Launch the API

```bash
uvicorn app.main:app --reload
```

Then visit <http://127.0.0.1:8000/docs> for interactive Swagger docs and sample requests.

## API Overview

| Endpoint | Method | Description |
| --- | --- | --- |
| `/` | GET | Health probe with app metadata.【F:app/main.py†L32-L41】 |
| `/movies/stats` | GET | Summarise the movies dataset (row counts, numeric statistics).【F:app/api/routers/movies.py†L12-L14】 |
| `/movies/top` | GET | Return top movies filtered by `limit` and `min_ratings` query parameters.【F:app/api/routers/movies.py†L17-L22】 |
| `/movies/{movie_id}/similar` | GET | Recommend movies sharing genres with the given title.【F:app/api/routers/movies.py†L25-L31】 |
| `/users/{user_id}/stats` | GET | Aggregate a user’s activity, genre preferences, and rating distribution.【F:app/api/routers/users.py†L15-L20】 |
| `/users/{user_id}/recommendations` | GET | Suggest unseen titles tailored to the user’s favourite genres.【F:app/api/routers/users.py†L23-L32】 |
| `/analytics/genre-trends` | GET | Genre-level averages and rating volumes.【F:app/api/routers/analytics.py†L31-L33】 |
| `/analytics/time-series` | GET | Daily average rating trends and activity counts.【F:app/api/routers/analytics.py†L36-L38】 |
| `/analytics/report` | GET | Generate charts and an HTML dashboard; returns filesystem path.【F:app/api/routers/analytics.py†L41-L46】 |

## Generating Reports

Calling `/analytics/report` will:

1. Create a ratings histogram and genre popularity bar chart with unique filenames under `reports/` to prevent collisions.【F:app/core/data_visualizer.py†L21-L66】
2. Assemble those assets into a self-contained HTML dashboard saved alongside the images.【F:app/core/data_visualizer.py†L67-L107】【F:app/services/report_service.py†L16-L33】

The response payload contains the path to the HTML file. Host the `reports/` directory with any static file server to share dashboards.

## Testing

Run the complete suite:

```bash
pytest
```

The tests exercise the FastAPI surface, analytics computations, and the recommender’s genre logic using small in-memory fixtures.【F:tests/test_main.py†L1-L15】【F:tests/integration/test_api_endpoints.py†L27-L70】

## Error Handling & Logging

Domain-specific exceptions translate into precise HTTP responses (422 for validation, 400 for domain errors, 500 for unexpected issues) and are logged with contextual metadata when raised.【F:app/main.py†L44-L151】 Logging is configured once at startup via `configure_logging()` for consistent formatting across the service.【F:app/main.py†L23-L28】【F:app/infrastructure/logging_config.py†L1-L8】

## Extending the Platform

- Swap the CSV loader for a database-backed implementation by providing a different `DatasetLoader` without touching the API layer.【F:app/api/dependencies.py†L1-L34】
- Replace `SimpleRecommender` with a model-based strategy while reusing validation and DTOs.【F:app/services/recommendation_service.py†L24-L37】【F:app/models/dto.py†L8-L74】
- Enhance dashboards by expanding `ReportService` or the `DataVisualizer` to include additional plots or export formats.【F:app/services/report_service.py†L16-L33】【F:app/core/data_visualizer.py†L21-L107】

Enjoy exploring movie data with a clean, test-driven toolkit! 🎥
