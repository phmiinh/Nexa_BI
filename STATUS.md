# SocialLens BI Status

Last updated: 2026-05-24 16:16 Asia/Ho_Chi_Minh

## Current Phase

Final technical delivery complete for the BI capstone MVP.

The project now runs as a YouTube-only real API BI workflow. Production/demo ETL uses `--no-sample-fallback`; sample data remains only for explicit dev/test scenarios.

## Completed

- Confirmed `SPEC.md` as the implementation source of truth.
- Scoped the project to F&B social media BI with Highlands Coffee as the primary brand, Phuc Long as an official YouTube competitor, and The Coffee House as lower-confidence query-filtered market mention data.
- Implemented Python ETL with YouTube extraction, raw JSONL storage, normalization, Vietnamese sentiment fallback, quality checks, processed CSV output, and PostgreSQL warehouse loading.
- Implemented PostgreSQL warehouse schema `social_dw`, star-style dimensions/facts, ETL run logging, analytical views, and SQL query files.
- Loaded the remote PostgreSQL warehouse at `172.16.4.81:5432/nexabi` using real YouTube API data only.
- Refreshed `dashboard/exports/*.csv` and `dashboard/exports/*.json` from warehouse views.
- Implemented Django API endpoints required by `SPEC.md`, including `GET /api/v1/analytics/insights/` and enriched `GET /api/v1/sync/status/`.
- Implemented the Next.js web dashboard pages: `/dashboard`, `/content`, `/sentiment`, `/competitors`, `/posts`, and `/data-health`.
- Synced frontend fallback JSON to the current warehouse/export result so offline demo data is also derived from real YouTube data.
- Added BI notebooks under `notebooks/` for quality, KPI baseline, content performance, posting heatmap, sentiment, competitor/SOV, and executive insights.
- Added Vietnamese insight document `docs/BI_Insights.md`.
- Added SQL validation document `docs/SQL_Validation_Result.md` and validation query `warehouse/queries/dashboard_validation.sql`.
- Updated the final run guide, Power BI build spec, and final technical checklist.
- Created dashboard screenshots under `dashboard/screenshots/`.
- Coordinated subagents by phase:
  - `analyst`: notebooks and Vietnamese BI insights.
  - `data-engineer`: SQL validation and dashboard KPI reconciliation.
  - `api-designer`: API insights/status contract.
  - `frontend-builder`: dashboard/data-health UI and fallback JSON.
  - `devops`: guide, Power BI build spec, final checklist.
  - `test-writer`: final delivery regression tests.

## Final Data Snapshot

| Metric | Value |
| --- | ---: |
| Platform scope | YouTube only |
| Fact posts | 65 |
| Fact sentiment comments | 15 |
| Date from | 2023-01-01 |
| Date to | 2026-05-19 |
| Total reach | 6,237,370 |
| Total engagement | 1,151 |
| Average engagement rate | 0.7435% |
| Average virality score | 0.0000% |
| Sample fallback in final ETL | Disabled |

## In Progress

- None for the current technical delivery.

## Blockers

- None for the remote PostgreSQL workflow.
- Power BI `.pbix` is not generated automatically because Power BI Desktop automation is not available in this environment. The build spec and exports are complete.

## Decisions

- Case study: F&B.
- Main brand: Highlands Coffee.
- Competitors: Phuc Long and The Coffee House.
- Primary platform: YouTube only.
- Facebook Graph API is out of MVP scope because it adds permission/App Review risk without improving the BI learning outcome enough for this capstone.
- Warehouse: PostgreSQL with schema `social_dw`.
- Dashboard deliverables: warehouse views, SQL validation, CSV/JSON exports, Power BI build guide, Next.js web demo, screenshots, notebooks, and Vietnamese insight document.
- The Coffee House official YouTube channel was not identified reliably, so its current data is query-filtered and documented as lower confidence.

## Deviations From SPEC

- Scope changed from Facebook + YouTube to YouTube-only by user decision on 2026-05-24.
- Earlier sample fallback for demo was replaced by production/demo `--no-sample-fallback` by user decision on 2026-05-24.
- Django API uses lightweight `JsonResponse` views instead of DRF; endpoint contract and BI data flow remain unchanged.
- Power BI `.pbix` is manual; the repo provides source views, exports, build spec, screenshots, and KPI validation.

## Verification

- `python -m etl.cli quality` -> passed.
- `python -m etl.cli export` -> exported all required dashboard views.
- `warehouse/queries/dashboard_validation.sql` via Python SQLAlchemy -> 42 validation rows, 25 PASS, 17 INFO, 0 FAIL.
- `python -m pytest -q` -> 32 passed.
- `python backend\manage.py check` -> pass.
- `cd frontend && npm run build` -> pass.
- API smoke:
  - `GET /api/v1/analytics/overview/` -> 200, `source=warehouse`, `total_posts=65`.
  - `GET /api/v1/analytics/insights/` -> 200, includes `freshness` and `source_confidence`.
  - `GET /api/v1/sync/status/` -> 200, warehouse counts `posts=65`, `comments=15`, platform `youtube`.
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
