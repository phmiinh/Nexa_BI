# SocialLens BI Run Guide

This guide describes how to run the project in its current MVP state.

Current status:

- ETL, sample fallback, quality checks, warehouse SQL, Django API, and Next.js dashboard are implemented.
- Power BI `.pbix` and final dashboard screenshots are still manual deliverables.
- PostgreSQL demo requires Docker Desktop to be running.

## 1. Prerequisites

Required:

- Python 3.10+; Python 3.12 is preferred.
- Node.js 20+ for the Next.js dashboard.
- Docker Desktop for PostgreSQL warehouse demo.

Optional:

- Facebook Graph API token.
- YouTube Data API key.
- Power BI Desktop.

## 2. Setup

From the repo root:

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

Install frontend dependencies:

```powershell
cd frontend
npm install
cd ..
```

Create local environment file:

```powershell
copy .env.example .env
```

Real API credentials are optional. If credentials are missing, ETL falls back to sample data.

## 3. Quick Run Without Docker

This path is enough to verify the current MVP without PostgreSQL.

Run sample ETL:

```powershell
python -m etl.cli run --sources sample --output-dir data\processed
```

Run data quality checks:

```powershell
python -m etl.cli quality --input-dir data\processed
```

Run tests:

```powershell
python -m pytest -q
```

Check Django API:

```powershell
python backend\manage.py check
```

Run Django API:

```powershell
python backend\manage.py runserver 0.0.0.0:8000
```

API endpoints include:

- `http://localhost:8000/health/`
- `http://localhost:8000/api/v1/posts/`
- `http://localhost:8000/api/v1/analytics/overview/`
- `http://localhost:8000/api/v1/analytics/engagement/`
- `http://localhost:8000/api/v1/analytics/sentiment/`
- `http://localhost:8000/api/v1/analytics/top-posts/`
- `http://localhost:8000/api/v1/analytics/content-performance/`
- `http://localhost:8000/api/v1/analytics/heatmap/`
- `http://localhost:8000/api/v1/analytics/competitors/`
- `http://localhost:8000/api/v1/sync/status/`

Run Next.js dashboard:

```powershell
cd frontend
$env:NEXT_PUBLIC_API_BASE_URL="http://localhost:8000"
npm run dev
```

Open:

- `http://localhost:3000/dashboard`
- `http://localhost:3000/content`
- `http://localhost:3000/sentiment`
- `http://localhost:3000/competitors`
- `http://localhost:3000/posts`
- `http://localhost:3000/data-health`

If `NEXT_PUBLIC_API_BASE_URL` is not set or the API is down, the frontend uses static fallback JSON.

## 4. Full Warehouse Run With Docker

Start Docker Desktop first.

Start PostgreSQL:

```powershell
docker compose up -d db
```

Run the full demo:

```powershell
make demo
```

Equivalent manual commands:

```powershell
python -m etl.cli run --sources facebook,youtube,sample --database-url "postgresql+psycopg://sociallens:sociallens_dev@localhost:5432/sociallens_bi"
python -m etl.cli quality --database-url "postgresql+psycopg://sociallens:sociallens_dev@localhost:5432/sociallens_bi"
python -m etl.cli export --database-url "postgresql+psycopg://sociallens:sociallens_dev@localhost:5432/sociallens_bi"
```

The warehouse schema is created automatically by the ETL loader from:

- `warehouse/schema/001_schema.sql`
- `warehouse/schema/002_indexes.sql`
- `warehouse/schema/003_views.sql`

Dashboard exports are written to:

- `dashboard/exports/`

## 5. Real API Run

Edit `.env`:

```env
FACEBOOK_ACCESS_TOKEN=...
FACEBOOK_PAGE_IDS=...
YOUTUBE_API_KEY=...
YOUTUBE_CHANNEL_IDS=...
YOUTUBE_QUERIES=
```

Run:

```powershell
python -m etl.cli run --sources facebook,youtube,sample --output-dir data\processed
```

If Facebook or YouTube credentials are missing or API calls fail, sample fallback keeps the demo runnable.

## 6. Frontend Build

```powershell
cd frontend
npm run build
```

The current verified routes are:

- `/`
- `/dashboard`
- `/content`
- `/sentiment`
- `/competitors`
- `/posts`
- `/data-health`

## 7. Power BI

Power BI is the primary dashboard deliverable for the BI assignment.

Preferred source:

- PostgreSQL schema `social_dw`
- Views:
  - `vw_executive_overview`
  - `vw_daily_engagement`
  - `vw_sentiment_trend`
  - `vw_content_performance`
  - `vw_competitor_benchmark`
  - `vw_posting_time_heatmap`
  - `vw_viral_posts`

Fallback source:

- CSV files in `dashboard/exports/`
- Processed CSV files in `data/processed/`

Power BI page plan is documented in:

- `dashboard/power_bi/README.md`

## 8. Useful Commands

```powershell
python -m pytest -q
python backend\manage.py check
python -m etl.cli run --sources sample --output-dir data\processed
python -m etl.cli quality --input-dir data\processed
cd frontend; npm run build
```

Makefile shortcuts:

```powershell
make setup
make db
make etl
make quality
make export
make test
make api-check
make frontend-build
make demo
```

On Windows, if `make` is unavailable, use the manual commands shown above.

## 9. Known Current Limitation

`docker compose up -d db` was not verified in the current environment because Docker Desktop was not running. The rest of the MVP was verified with:

- `python -m pytest -q` -> 19 passed
- `python backend\manage.py check` -> passed
- `python -m etl.cli run --sources sample --output-dir data\processed` -> passed
- `python -m etl.cli quality --input-dir data\processed` -> passed
- `cd frontend && npm run build` -> passed
