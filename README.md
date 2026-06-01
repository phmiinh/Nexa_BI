# SocialLens BI

Business Intelligence capstone for F&B social media analytics.

Current implementation is a YouTube-only BI workflow for Highlands Coffee and selected F&B competitors. The runtime source of truth is the PostgreSQL warehouse schema `social_dw`; the Next.js dashboard and Django API read from PostgreSQL, not from mock JSON files.

## Current Status

Last reviewed: 2026-06-01 Asia/Ho_Chi_Minh.

| Area | Status |
| --- | --- |
| Scope | F&B, YouTube official channels only |
| Primary brand | Highlands Coffee Vietnam |
| Competitor set | Trung Nguyen Legend, Phuc Long, Cong Caphe, Cheese Coffee, KOI The Vietnam, Gong Cha Vietnam, Starbucks Vietnam |
| Source of truth | PostgreSQL `social_dw` |
| Runtime mock fallback | Removed |
| Data quality gate | `26 PASS`, `17 INFO`, `0 FAIL` |
| Power BI `.pbix` | Manual artifact, build from `dashboard/power_bi/README.md` |

Final warehouse snapshot after official-only cleanup:

| Metric | Value |
| --- | ---: |
| Fact posts | 817 |
| Fact sentiment comments | 1,526 |
| Pages in active BI views | 8 |
| Date from | 2017-09-26 |
| Date to | 2026-05-26 |
| Total reach / views proxy | 167,066,949 |
| Total engagement | 48,325 |
| Average engagement rate | 1.9164% |
| Average virality score | 0.0000% |

Notes:

- `reach` is a YouTube views/impressions proxy, not unique reach.
- `virality_score` is currently 0 because YouTube does not expose share counts through this pipeline.
- Broad curated query data was rejected due noise. A cleanup on 2026-06-01 removed 59 lower-confidence query residual posts, 166 comments, and 41 orphan pages. The removed rows are archived under `data/processed_archive/`.

## Architecture

```text
YouTube Data API v3
        |
        v
Python ETL: extract -> normalize -> sentiment -> quality -> load
        |
        v
PostgreSQL warehouse: social_dw dimensions, facts, analytical views
        |
        +--> Django API: backend/sociallens_api
        |
        +--> dashboard/exports CSV/JSON
        |
        +--> Next.js dashboard and Power BI
```

Implementation deviations from the planning docs:

- `ROADMAP.md` and `DESIGN.md` describe the broader target architecture. The delivered MVP intentionally narrows runtime ingestion to YouTube official channels.
- The backend uses lightweight Django `JsonResponse` views, not DRF/Celery.
- The frontend uses Next.js App Router with plain CSS components, not Tailwind/Recharts.
- Sample data remains available for dev/test only; it is not a final runtime fallback.

## Repository Layout

```text
backend/sociallens_api/       Django API backed by PostgreSQL views
etl/                          Python ETL package and CLI
warehouse/schema/             PostgreSQL schema, indexes, analytical views
warehouse/queries/            Validation SQL
frontend/                     Next.js web dashboard
dashboard/exports/            CSV/JSON exports generated from warehouse views
dashboard/power_bi/           Power BI build guide and final .pbix location
dashboard/screenshots/        Dashboard evidence screenshots
docs/                         BI insights, SQL validation, final checklist
notebooks/                    BI analysis notebooks
tests/                        Python regression tests and contract checks
```

## Environment

Create `.env` from `.env.example` and set local values:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/nexabi
SOCIALENS_DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/nexabi
YOUTUBE_API_KEY=...
YOUTUBE_CHANNEL_IDS=...
YOUTUBE_QUERIES=
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Do not commit `.env` or secrets.

Load `.env` into PowerShell before manual commands:

```powershell
Get-Content .env | Where-Object { $_ -match '^[A-Za-z_][A-Za-z0-9_]*=' } | ForEach-Object {
  $name, $value = $_ -split '=', 2
  Set-Item -Path "Env:$name" -Value $value
}
```

## Setup

Python:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

Frontend:

```powershell
cd frontend
npm install
cd ..
```

## ETL and Warehouse

Run the official-channel ETL when the YouTube API key/quota is available:

```powershell
python -m etl.cli run --sources youtube --channel-ids $env:YOUTUBE_CHANNEL_IDS --queries= --limit 50 --comments-limit 100 --max-search-pages 12 --database-url $env:DATABASE_URL
```

Quality gate:

```powershell
python -m etl.cli quality --database-url $env:DATABASE_URL
```

Export warehouse views:

```powershell
python -m etl.cli export --database-url $env:DATABASE_URL
```

Make shortcuts, if `make` is available:

```powershell
make etl
make quality
make export
make demo
```

## API

Run Django:

```powershell
python backend\manage.py runserver 127.0.0.1:8000
```

Key endpoints:

```text
GET /health/
GET /api/v1/posts/
GET /api/v1/posts/{post_id}/
GET /api/v1/analytics/overview/
GET /api/v1/analytics/engagement/?limit=120
GET /api/v1/analytics/sentiment/?limit=120
GET /api/v1/analytics/top-posts/
GET /api/v1/analytics/content-performance/
GET /api/v1/analytics/heatmap/
GET /api/v1/analytics/competitors/
GET /api/v1/analytics/insights/
GET /api/v1/sync/status/
```

Warehouse errors are sanitized for clients; internal exception details are logged server-side.

## Web Dashboard

Run the Next.js dashboard:

```powershell
cd frontend
$env:NEXT_PUBLIC_API_BASE_URL="http://localhost:8000"
npm run dev
```

Routes:

```text
http://localhost:3000/dashboard
http://localhost:3000/content
http://localhost:3000/sentiment
http://localhost:3000/competitors
http://localhost:3000/posts
http://localhost:3000/data-health
```

The frontend uses API data only. Static mock JSON under `frontend/src/data` was removed and is guarded by tests.

## Power BI

Power BI is the primary submission dashboard artifact.

Preferred connection:

- PostgreSQL database `nexabi`
- Schema `social_dw`
- Views documented in `dashboard/power_bi/README.md`

Backup source:

- CSV files in `dashboard/exports/`

Expected manual artifact:

- Save the final `.pbix` under `dashboard/power_bi/`.
- Refresh screenshots under `dashboard/screenshots/` after the final warehouse/export refresh.

## Validation

Current regression suite:

```powershell
python -m pytest -q
python backend\manage.py check
cd frontend
npm test -- --runInBand
npm run build
npm audit --omit=dev --audit-level=moderate
cd ..
python -m etl.cli quality --database-url $env:DATABASE_URL
```

Expected current results:

- Python tests: `56 passed, 1 skipped`.
- Frontend tests: `7 passed`.
- Django check: no issues.
- Next.js build: pass.
- Production npm audit: `0 vulnerabilities`.
- Warehouse quality: `26 PASS`, `17 INFO`, `0 FAIL`.

Optional live YouTube contract test:

```powershell
$env:RUN_YOUTUBE_LIVE_TESTS="1"
python -m pytest tests/test_youtube_live_contract.py -q
```

This test is skipped when the YouTube key/quota is not available.

## BI Deliverables

- `docs/BI_Insights.md`: Vietnamese BI insight summary.
- `docs/SQL_Validation_Result.md`: warehouse validation result.
- `dashboard/exports/`: latest warehouse exports.
- `dashboard/power_bi/README.md`: Power BI build specification.
- `docs/Final_Checklist.md`: final handoff checklist.
- `STATUS.md`: current implementation status and known limitations.

## Known Limitations

- The current production warehouse is YouTube-only.
- The Coffee House official YouTube channel was not reliably identified, so it is not included in the cleaned official-channel warehouse.
- Sentiment uses a lightweight Vietnamese keyword/rule fallback and should be presented as a directional signal, not a manually validated NLP benchmark.
- Forecasting, clustering, demographic analysis, and follower growth from the original roadmap are not productionized in this MVP.
- Power BI `.pbix` generation is manual because Power BI Desktop automation is not available in this environment.

## License

Academic project for Business Intelligence coursework.
