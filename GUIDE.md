# SocialLens BI Final Run Guide

This guide is the final technical delivery runbook for SocialLens BI.

Final delivery status:

- ETL uses real YouTube data only for demo and warehouse runs.
- Sample fallback is disabled with `--no-sample-fallback` for final ETL.
- Remote PostgreSQL is the preferred warehouse path.
- Dashboard exports are generated from PostgreSQL views into `dashboard/exports/`.
- Power BI is the primary BI dashboard deliverable; the Next.js dashboard is the companion web dashboard.

## 1. Prerequisites

Required:

- Python 3.10+; Python 3.12 is preferred.
- Node.js 20+ for the Next.js dashboard.
- Access to the remote PostgreSQL database.
- A valid `YOUTUBE_API_KEY`.

Optional:

- Power BI Desktop.
- Docker Desktop for local PostgreSQL only.
- `make`. If unavailable on Windows, use the PowerShell commands in this guide.

## 2. Environment Setup

From the repo root:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

Install frontend dependencies:

```powershell
cd frontend
npm install
cd ..
```

Create a local environment file:

```powershell
copy .env.example .env
```

Set the final remote PostgreSQL and YouTube values in `.env`:

```env
POSTGRES_HOST=172.16.4.81
POSTGRES_PORT=5432
POSTGRES_DB=nexabi
POSTGRES_USER=next
POSTGRES_PASSWORD=...
DATABASE_URL=postgresql+psycopg://next:...@172.16.4.81:5432/nexabi
SOCIALENS_DATABASE_URL=postgresql+psycopg://next:...@172.16.4.81:5432/nexabi
YOUTUBE_API_KEY=...
YOUTUBE_CHANNEL_IDS=UCHEqa2uTf8uXrGWrnU3ThgA,UCq6WR0wWNUuz53c4zeWSa8g
YOUTUBE_QUERIES=The Coffee House Vietnam
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Do not commit `.env` or secrets.

## 3. Load `.env` in PowerShell

Use this once per PowerShell session before running manual commands:

```powershell
Get-Content .env | Where-Object { $_ -match '^[A-Za-z_][A-Za-z0-9_]*=' } | ForEach-Object {
  $name, $value = $_ -split '=', 2
  Set-Item -Path "Env:$name" -Value $value
}
```

Confirm required values are present:

```powershell
$env:DATABASE_URL
$env:YOUTUBE_API_KEY
```

## 4. Final ETL, Quality, and Export Run

Use this PowerShell sequence for the final technical delivery:

```powershell
python -m etl.cli run --sources youtube --no-sample-fallback --database-url $env:DATABASE_URL
python -m etl.cli quality --database-url $env:DATABASE_URL
python -m etl.cli export --database-url $env:DATABASE_URL
```

Expected result:

- ETL fails if `YOUTUBE_API_KEY` is missing or the live YouTube request cannot produce data.
- Warehouse tables and views are created in PostgreSQL schema `social_dw`.
- CSV and JSON dashboard exports are written to `dashboard/exports/`.

Export files:

- `dashboard/exports/vw_executive_overview.csv`
- `dashboard/exports/vw_daily_engagement.csv`
- `dashboard/exports/vw_sentiment_trend.csv`
- `dashboard/exports/vw_content_performance.csv`
- `dashboard/exports/vw_competitor_benchmark.csv`
- `dashboard/exports/vw_posting_time_heatmap.csv`
- `dashboard/exports/vw_viral_posts.csv`

If `make` is available, the equivalent shortcut is:

```powershell
make demo
```

Individual targets are:

```powershell
make etl
make quality
make export
```

## 5. Validation Commands

Run these checks before recording the final demo:

```powershell
python -m pytest -q
python backend\manage.py check
cd frontend
npm run build
cd ..
```

If Power BI numbers need SQL confirmation, query the remote warehouse views under `social_dw`.

## 6. API Server

Start Django after loading `.env`:

```powershell
python backend\manage.py runserver 0.0.0.0:8000
```

Final API base URL:

- `http://localhost:8000`

Useful endpoints:

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

## 7. Next.js Dashboard

Start the dashboard in a second PowerShell session:

```powershell
cd frontend
$env:NEXT_PUBLIC_API_BASE_URL="http://localhost:8000"
npm run dev
```

Final dashboard URL:

- `http://localhost:3000/dashboard`

Additional verified routes:

- `http://localhost:3000/content`
- `http://localhost:3000/sentiment`
- `http://localhost:3000/competitors`
- `http://localhost:3000/posts`
- `http://localhost:3000/data-health`

The frontend has static fallback JSON for development, but the final delivery should be demonstrated with the Django API running against the remote PostgreSQL warehouse.

## 8. Power BI Build

Power BI is the primary dashboard artifact for submission.

Preferred source:

- PostgreSQL host from `.env`
- Database `nexabi`
- Schema `social_dw`
- Views documented in `dashboard/power_bi/README.md`

Backup source:

- CSV exports in `dashboard/exports/`

Expected Power BI artifact:

- Save the `.pbix` file in `dashboard/power_bi/`.
- Capture final dashboard screenshots in `dashboard/screenshots/`.

## 9. Local Sample Path

Use this only for development or tests without PostgreSQL and without external API calls:

```powershell
python -m etl.cli run --sources sample --output-dir data\processed
python -m etl.cli quality --input-dir data\processed
```

Do not use sample output for the final technical delivery.

## 10. Local Docker PostgreSQL

Remote PostgreSQL is the final delivery path. Local Docker is optional for development:

```powershell
docker compose up -d db
python -m etl.cli run --sources youtube --no-sample-fallback --database-url $env:DATABASE_URL
python -m etl.cli quality --database-url $env:DATABASE_URL
python -m etl.cli export --database-url $env:DATABASE_URL
```

## 11. Final Evidence

Collect these before submission:

- Terminal output showing successful real YouTube ETL with `--no-sample-fallback`.
- Terminal output showing successful quality checks.
- `dashboard/exports/` CSV files refreshed from the remote warehouse.
- Power BI `.pbix` saved under `dashboard/power_bi/`.
- Screenshots saved under `dashboard/screenshots/`.
- API URL and dashboard URL listed in the final report.
- Final checklist completed in `docs/Final_Checklist.md`.
