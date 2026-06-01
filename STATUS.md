# SocialLens BI Status

Last updated: 2026-06-01 23:38 Asia/Ho_Chi_Minh

## Current Phase

Final technical delivery refreshed for the BI capstone MVP.

The project now runs as a YouTube-only official-channel BI workflow. Automatic sample fallback has been removed; sample data remains only for explicit dev/test scenarios. PostgreSQL schema `social_dw` is the runtime source of truth.

## Completed

- Confirmed `ROADMAP.md` and `DESIGN.md` as planning sources, with documented MVP deviations for the final implementation.
- Scoped the project to F&B social media BI with Highlands Coffee as the primary brand and a curated official-channel competitor set.
- Implemented Python ETL with quota-efficient YouTube uploads playlist extraction for official channels, raw JSONL storage, normalization, Vietnamese sentiment fallback, quality checks, processed CSV output, and PostgreSQL warehouse loading.
- Implemented PostgreSQL warehouse schema `social_dw`, star-style dimensions/facts, ETL run logging, analytical views, and SQL query files.
- Loaded the remote PostgreSQL warehouse using real YouTube API data only.
- Removed broad/query residual rows from the warehouse on 2026-06-01 so active BI views match the accepted official-channel batch.
- Archived removed lower-confidence query residual rows under `data/processed_archive/`.
- Refreshed `dashboard/exports/*.csv` and `dashboard/exports/*.json` from warehouse views after cleanup.
- Implemented Django API endpoints required by the BI dashboard, including `GET /api/v1/analytics/insights/` and enriched `GET /api/v1/sync/status/`.
- Implemented the Next.js web dashboard pages: `/dashboard`, `/content`, `/sentiment`, `/competitors`, `/posts`, and `/data-health`.
- Removed frontend fallback JSON; the web dashboard now uses the Django API backed by PostgreSQL as the single source of truth.
- Added BI notebooks under `notebooks/` for quality, KPI baseline, content performance, posting heatmap, sentiment, competitor/SOV, and executive insights.
- Added Vietnamese insight document `docs/BI_Insights.md`.
- Added SQL validation document `docs/SQL_Validation_Result.md` and validation query `warehouse/queries/dashboard_validation.sql`.
- Added Python regression tests, frontend Jest/React Testing Library tests, static frontend no-mock guard, and optional live YouTube contract test.
- Updated the final run guide, Power BI build spec, final technical checklist, and README.

## Final Data Snapshot

| Metric | Value |
| --- | ---: |
| Platform scope | YouTube only |
| Active BI pages | 8 |
| Fact posts | 817 |
| Fact sentiment comments | 1,526 |
| Date from | 2017-09-26 |
| Date to | 2026-05-26 |
| Total reach / views proxy | 167,066,949 |
| Total engagement | 48,325 |
| Average engagement rate | 1.9164% |
| Average virality score | 0.0000% |
| Automatic sample fallback in final ETL | Removed |

## Active Pages

| Page | Posts | Comments |
| --- | ---: | ---: |
| Trung Nguyen Legend | 600 | 1,258 |
| Highlands Coffee Vietnam | 123 | 240 |
| Phuc Long | 35 | 9 |
| Cong Caphe | 31 | 12 |
| Cheese Coffee | 22 | 2 |
| KOI The Vietnam | 3 | 0 |
| Gong Cha Vietnam | 2 | 4 |
| Starbucks Viet Nam | 1 | 1 |

## In Progress

- None for the current technical delivery.

## Blockers

- None for the remote PostgreSQL/API/web dashboard workflow.
- Power BI `.pbix` is not generated automatically because Power BI Desktop automation is not available in this environment. The build spec and exports are complete.

## Decisions

- Case study: F&B.
- Main brand: Highlands Coffee.
- Primary platform: YouTube only.
- Official-channel data is preferred over query-search data for warehouse truth.
- Facebook Graph API is out of MVP scope because it adds permission/App Review risk without improving the BI learning outcome enough for this capstone.
- Warehouse: PostgreSQL with schema `social_dw`.
- Dashboard deliverables: warehouse views, SQL validation, CSV/JSON exports, Power BI build guide, Next.js web demo, screenshots, notebooks, and Vietnamese insight document.
- The Coffee House official YouTube channel was not identified reliably, so it is not included in the cleaned official-channel warehouse.
- Broad curated query batch was rejected on 2026-05-31 because it introduced 502 new non-official pages and 98.76% non-official reach.
- On 2026-06-01, cleanup removed 59 lower-confidence query residual posts, 166 comments, and 41 orphan pages; active warehouse views now match the accepted official-channel batch.

## Deviations From Planning Docs

- Scope changed from Facebook + YouTube to YouTube-only by user decision on 2026-05-24.
- Earlier sample fallback for demo was removed; final ETL fails clearly if real YouTube extraction cannot run.
- Django API uses lightweight `JsonResponse` views instead of DRF; endpoint contract and BI data flow remain unchanged.
- Power BI `.pbix` is manual; the repo provides source views, exports, build spec, screenshots, and KPI validation.
- Frontend static fallback JSON has been removed; PostgreSQL via Django API is now the only runtime BI data source for the web dashboard.
- The frontend uses plain CSS/React components rather than Tailwind/Recharts from the aspirational design document.

## Verification

- `python -m etl.cli quality --database-url $env:DATABASE_URL` -> 43 validation rows, 26 PASS, 17 INFO, 0 FAIL.
- `python -m etl.cli export` -> exported all required dashboard views.
- `warehouse/queries/dashboard_validation.sql` via Python SQLAlchemy -> 43 validation rows, 26 PASS, 17 INFO, 0 FAIL.
- `python -m pytest -q` -> 56 passed, 1 skipped.
- `python backend\manage.py check` -> pass.
- `cd frontend && npm test -- --runInBand` -> 7 passed.
- `cd frontend && npm run build` -> pass.
- `cd frontend && npm audit --omit=dev --audit-level=moderate` -> 0 vulnerabilities.
- API smoke:
  - `GET /api/v1/analytics/overview/` -> 200, `source=warehouse`, `total_posts=817`.
  - `GET /api/v1/analytics/insights/` -> 200, includes `freshness` and `source_confidence`.
  - `GET /api/v1/sync/status/` -> 200, warehouse counts `posts=817`, `comments=1526`, latest source `maintenance:official-only-cleanup`.
- Next smoke:
  - `/dashboard` -> 200.
  - `/content` -> 200.
  - `/sentiment` -> 200.
  - `/competitors` -> 200.
  - `/posts` -> 200.
  - `/data-health` -> 200.

## Next Steps

- Build the final `.pbix` manually in Power BI Desktop using `dashboard/power_bi/README.md`.
- Refresh final screenshots after the `.pbix` or web dashboard is opened against the cleaned warehouse.
- Write the long final report if required by the course submission format.
- Revisit The Coffee House only if a reliable official YouTube channel ID becomes available.
