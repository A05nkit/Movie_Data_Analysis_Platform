# 🎬 Movie Data Analysis Platform

A FastAPI-powered service that loads MovieLens-style CSV files, cleans and validates them with pandas, and exposes movie analytics, personalized insights, and recommendation endpoints. The project emphasises a layered architecture, thorough validation, and reproducible visual reports.

## Features

- **Data ingestion & hygiene** – Load CSV assets from the configurable `data/` directory, drop duplicates, and enforce schema integrity for the movies and ratings datasets before any computation runs.【app/core/data_processor.py】【app/infrastructure/dataset_loader.py】
- **Exploratory analytics** – Produce dataset summaries, top-movie leaderboards, genre trends, user statistics, and time-series metrics through the `MovieAnalyzer` service layer.【app/services/analysis_service.py】【app/core/movie_analyzer.py】
- **Explainable recommendations** – Generate similar-movie suggestions and user-tailored picks via a genre-overlap recommender that honours validation and referential integrity checks.【app/services/recommendation_service.py】【app/core/recommender.py†L11-L173】
- **Automated reporting** – Build PNG visualisations and an HTML dashboard with collision-resistant filenames so concurrent requests never overwrite prior output.【app/core/data_visualizer.py】【app/services/report_service.py】
- **Robust API surface** – FastAPI routers expose analytics, movies, and user endpoints, while the application maps domain exceptions to clear HTTP responses.【app/api/routers/movies.py】【app/api/routers/users.py】【app/api/routers/analytics.py†L31-L46】【app/main.py】
- **Confidence via tests** – Unit and integration suites cover the API contract, core analytics, and recommender behaviour using FastAPI’s TestClient and in-memory dataframes.【tests/test_main.py】【tests/integration/test_api_endpoints.py】

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

All paths default to the bundled `data/` and `reports/` folders, and can be overridden with environment variables prefixed by `MOVIE_APP_` (e.g., `MOVIE_APP_DATA_FOLDER=/path/to/csvs`).【app/config/settings.py†L6-L21】

### 4. Launch the API

```bash
uvicorn app.main:app --reload
```

Then visit <http://127.0.0.1:8000/docs> for interactive Swagger docs and sample requests.

## API Overview

| Endpoint                           | Method | Description                                                                                                    |
| ---------------------------------- | ------ | -------------------------------------------------------------------------------------------------------------- |
| `/`                                | GET    | Health probe with app metadata.【app/main.py†L32-L41】                                                         |
| `/movies/stats`                    | GET    | Summarise the movies dataset (row counts, numeric statistics).【app/api/routers/movies.py†L12-L14】            |
| `/movies/top`                      | GET    | Return top movies filtered by `limit` and `min_ratings` query parameters.【app/api/routers/movies.py†L17-L22】 |
| `/movies/{movie_id}/similar`       | GET    | Recommend movies sharing genres with the given title.【app/api/routers/movies.py†L25-L31】                     |
| `/users/{user_id}/stats`           | GET    | Aggregate a user’s activity, genre preferences, and rating distribution.【app/api/routers/users.py†L15-L20】   |
| `/users/{user_id}/recommendations` | GET    | Suggest unseen titles tailored to the user’s favourite genres.【app/api/routers/users.py†L23-L32】             |
| `/analytics/genre-trends`          | GET    | Genre-level averages and rating volumes.【app/api/routers/analytics.py†L31-L33】                               |
| `/analytics/time-series`           | GET    | Daily average rating trends and activity counts.【app/api/routers/analytics.py†L36-L38】                       |
| `/analytics/report`                | GET    | Generate charts and an HTML dashboard; returns filesystem path.【app/api/routers/analytics.py†L41-L46】        |

## Generating Reports

Calling `/analytics/report` will:

1. Create a ratings histogram and genre popularity bar chart with unique filenames under `reports/` to prevent collisions.【app/core/data_visualizer.py†L21-L66】
2. Assemble those assets into a self-contained HTML dashboard saved alongside the images.【app/core/data_visualizer.py†L67-L107】【app/services/report_service.py†L16-L33】

The response payload contains the path to the HTML file. Host the `reports/` directory with any static file server to share dashboards.

## Testing

Run the complete suite:

```bash
pytest
```

The tests exercise the FastAPI surface, analytics computations, and the recommender’s genre logic using small in-memory fixtures.【tests/test_main.py】【tests/integration/test_api_endpoints.py】

## Error Handling & Logging

Domain-specific exceptions translate into precise HTTP responses (422 for validation, 400 for domain errors, 500 for unexpected issues) and are logged with contextual metadata when raised.【app/main.py†L44-L151】 Logging is configured once at startup via `configure_logging()` for consistent formatting across the service.【app/main.py†L23-L28】【app/infrastructure/logging_config.py†L1-L8】

## Extending the Platform

- Swap the CSV loader for a database-backed implementation by providing a different `DatasetLoader` without touching the API layer.【app/api/dependencies.py†L1-L34】
- Replace `SimpleRecommender` with a model-based strategy while reusing validation and DTOs.【app/services/recommendation_service.py†L24-L37】【app/models/dto.py†L8-L74】
- Enhance dashboards by expanding `ReportService` or the `DataVisualizer` to include additional plots or export formats.【app/services/report_service.py†L16-L33】【app/core/data_visualizer.py】

# Personal Note

## AI Tools Used

I used following AI tool for my work.

- ChatGPT (OpenAI)
- Codex (OpenAI)

## Prompts

initially I gave prompt like -

-"Generate a FastAPI project skeleton for a Movie Data Analysis Platform with folders for core, services, infrastructure, api, and tests. Include classes for DataProcessor, MovieAnalyzer, SimpleRecommender, and DataVisualizer. Each should have placeholder methods (load_data, analyze_genre_trends, etc.). Add main.py, config file, and one example test."

- "I took help to generate test cases, and asked to cover all possible edge cases, also make sure coverage is more than 98%."
- "Reviewed my code for issues and improvements following best practices."

## Overall Approach

I used AI to:

- Build the initial structure of the project and define module boundaries
- Generate test cases for edge scenarios, achieving 99% coverage
- Improve documentation quality and readability of the README and comments
- Perform code review via Codex and identify potential architectural and concurrency issues

## Modifications & Improvements

Based on Codex's review, I made key fixes:

- Added data validation within RecommendationService to ensure consistent data integrity
- Updated report generation logic to prevent overwriting of chart files by using unique filenames per report
- Enhanced comments, formatting, and readability for better maintainability
