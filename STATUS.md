# SocialLens BI Status

Last updated: 2026-05-31 23:35 Asia/Ho_Chi_Minh

## Current Phase

Final technical delivery refreshed for the BI capstone MVP.

The project now runs as a YouTube-only real API BI workflow. Automatic sample fallback has been removed; sample data remains only for explicit dev/test scenarios.

## Completed

- Confirmed `SPEC.md` as the implementation source of truth.
- Scoped the project to F&B social media BI with Highlands Coffee as the primary brand and a wider competitor set: Phuc Long, The Coffee House, Trung Nguyen Legend, Cong Caphe, Starbucks Vietnam, Gong Cha Vietnam, Cheese Coffee, and KOI The Vietnam.
- Implemented Python ETL with quota-efficient YouTube uploads playlist extraction for official channels, raw JSONL storage, normalization, Vietnamese sentiment fallback, quality checks, processed CSV output, and PostgreSQL warehouse loading.
- Implemented PostgreSQL warehouse schema `social_dw`, star-style dimensions/facts, ETL run logging, analytical views, and SQL query files.
- Loaded the remote PostgreSQL warehouse at `172.16.4.81:5432/nexabi` using real YouTube API data only.
- Refreshed `dashboard/exports/*.csv` and `dashboard/exports/*.json` from warehouse views after the official-channel batch.
- Implemented Django API endpoints required by `SPEC.md`, including `GET /api/v1/analytics/insights/` and enriched `GET /api/v1/sync/status/`.
- Implemented the Next.js web dashboard pages: `/dashboard`, `/content`, `/sentiment`, `/competitors`, `/posts`, and `/data-health`.
- Removed frontend fallback JSON; the web dashboard now uses the Django API backed by PostgreSQL as the single source of truth.
- Added BI notebooks under `notebooks/` for quality, KPI baseline, content performance, posting heatmap, sentiment, competitor/SOV, and executive insights.
- Added Vietnamese insight document `docs/BI_Insights.md`.
- Added SQL validation document `docs/SQL_Validation_Result.md` and validation query `warehouse/queries/dashboard_validation.sql`.
- Updated the final run guide, Power BI build spec, and final technical checklist.
- Created dashboard screenshots under `dashboard/screenshots/`.
- Coordinated subagents by phase:
  - `analyst`: notebooks and Vietnamese BI insights.
  - `data-engineer`: SQL validation and dashboard KPI reconciliation.
  - `api-designer`: API insights/status contract.
  - `frontend-builder`: dashboard/data-health UI.
  - `devops`: guide, Power BI build spec, final checklist.
  - `test-writer`: final delivery regression tests.

## Final Data Snapshot

| Metric | Value |
| --- | ---: |
| Platform scope | YouTube only |
| Fact posts | 876 |
| Fact sentiment comments | 1,692 |
| Date from | 2017-09-26 |
| Date to | 2026-05-31 |
| Total reach | 167,400,096 |
| Total engagement | 53,845 |
| Average engagement rate | 1.8806% |
| Average virality score | 0.0000% |
| Automatic sample fallback in final ETL | Removed |

## In Progress

- None for the current technical delivery.

## Blockers

- None for the remote PostgreSQL workflow.
- Power BI `.pbix` is not generated automatically because Power BI Desktop automation is not available in this environment. The build spec and exports are complete.

## Decisions

- Case study: F&B.
- Main brand: Highlands Coffee.
- Competitors: Phuc Long, The Coffee House, Trung Nguyen Legend, Cong Caphe, Starbucks Vietnam, Gong Cha Vietnam, Cheese Coffee, and KOI The Vietnam.
- Primary platform: YouTube only.
- Facebook Graph API is out of MVP scope because it adds permission/App Review risk without improving the BI learning outcome enough for this capstone.
- Warehouse: PostgreSQL with schema `social_dw`.
- Dashboard deliverables: warehouse views, SQL validation, CSV/JSON exports, Power BI build guide, Next.js web demo, screenshots, notebooks, and Vietnamese insight document.
- The Coffee House official YouTube channel was not identified reliably, so its current data remains query-filtered and documented as lower confidence.
- Broad curated query batch was rejected on 2026-05-31 because it introduced 502 new non-official pages and 98.76% non-official reach. The accepted refresh uses official channels only.

## Deviations From SPEC

- Scope changed from Facebook + YouTube to YouTube-only by user decision on 2026-05-24.
- Earlier sample fallback for demo was removed; final ETL fails clearly if real YouTube extraction cannot run.
- Django API uses lightweight `JsonResponse` views instead of DRF; endpoint contract and BI data flow remain unchanged.
- Power BI `.pbix` is manual; the repo provides source views, exports, build spec, screenshots, and KPI validation.
- Frontend static fallback JSON has been removed; PostgreSQL via Django API is now the only runtime BI data source for the web dashboard.

## Verification

- `python -m etl.cli quality --database-url $env:DATABASE_URL` -> 42 validation rows, 25 PASS, 17 INFO, 0 FAIL.
- `python -m etl.cli export` -> exported all required dashboard views.
- `warehouse/queries/dashboard_validation.sql` via Python SQLAlchemy -> 42 validation rows, 25 PASS, 17 INFO, 0 FAIL.
- `python -m pytest -q` -> 42 passed.
- `python backend\manage.py check` -> pass.
- `cd frontend && npm run build` -> pass.
- API smoke:
  - `GET /api/v1/analytics/overview/` -> 200, `source=warehouse`, `total_posts=876`.
  - `GET /api/v1/analytics/insights/` -> 200, includes `freshness` and `source_confidence`.
  - `GET /api/v1/sync/status/` -> 200, warehouse counts `posts=876`, `comments=1692`, latest source `etl.cli:youtube:official-a2`.
- Next smoke:
  - `/dashboard` -> 200.
  - `/content` -> 200.
  - `/sentiment` -> 200.
  - `/competitors` -> 200.
  - `/posts` -> 200.
  - `/data-health` -> 200.
- Screenshots created:
  - `dashboard/screenshots/dashboard.png`
  - `dashboard/screenshots/content.png`
  - `dashboard/screenshots/sentiment.png`
  - `dashboard/screenshots/competitors.png`
  - `dashboard/screenshots/posts.png`
  - `dashboard/screenshots/data-health.png`

## Next Steps

- Build the final `.pbix` manually in Power BI Desktop using `dashboard/power_bi/README.md`.
- Write the long final report if required by the course submission format.
- Revisit The Coffee House if a reliable official YouTube channel ID becomes available.
