# SocialLens BI Implementation Specification

This file records the implemented MVP contract derived from `ROADMAP.md` and `DESIGN.md`.
Those documents remain the planning source, but the final delivery intentionally narrows scope where needed for a reliable BI capstone handoff.

## Scope

- Industry: F&B.
- Primary brand: Highlands Coffee Vietnam.
- Runtime platform: YouTube only.
- Runtime data source: real YouTube API data from approved official channels.
- Source of truth: PostgreSQL warehouse schema `social_dw`.
- Sample data: dev/test only, never an automatic runtime fallback.
- Power BI: primary BI dashboard deliverable.
- Next.js: companion web dashboard.

Approved active YouTube pages:

- Highlands Coffee Vietnam.
- Trung Nguyen Legend.
- Phuc Long.
- Cong Caphe.
- Cheese Coffee.
- KOI The Vietnam.
- Gong Cha Vietnam.
- Starbucks Viet Nam.

The Coffee House is excluded from the cleaned official-channel warehouse until a reliable official YouTube channel ID is available.

## Data Contract

Required warehouse facts:

- `social_dw.fact_post`: one row per YouTube video/post.
- `social_dw.fact_sentiment`: one row per loaded comment with sentiment.

Required warehouse dimensions:

- `social_dw.dim_time`
- `social_dw.dim_platform`
- `social_dw.dim_content_type`
- `social_dw.dim_page`

Required analytical views:

- `vw_executive_overview`
- `vw_daily_engagement`
- `vw_sentiment_trend`
- `vw_content_performance`
- `vw_competitor_benchmark`
- `vw_posting_time_heatmap`
- `vw_viral_posts`

Natural key rules:

- Posts deduplicate by `(platform_id, external_post_id)`.
- Comments deduplicate by `(platform_id, external_comment_id)`.
- ETL should upsert existing rows and avoid duplicate fact records.

## KPI Definitions

- `engagement_count = likes + comments + shares + saves`
- `engagement_rate = engagement_count / reach * 100`
- `virality_score = shares / reach * 100`
- `sentiment_ratio = positive_comments / total_comments * 100`
- `share_of_voice = page reach / total scoped reach * 100`

MVP caveats:

- YouTube `reach` is treated as a views/impressions proxy, not unique reach.
- YouTube share counts are unavailable, so `virality_score` is expected to be `0.0000%`.
- Share of voice is reach-based for the scoped official-channel warehouse.
- Sentiment is a lightweight Vietnamese rule fallback and should be presented as a directional BI signal.

## ETL Contract

Final ETL must:

- Use YouTube official channel extraction through `channels.list -> uploads playlist -> playlistItems.list -> videos.list`.
- Keep query-search extraction available only for probes or explicitly lower-confidence experiments.
- Fail clearly when production YouTube config or API calls are unavailable.
- Store raw JSONL data under `data/raw/`.
- Write processed CSVs under `data/processed/`.
- Load PostgreSQL via `python -m etl.cli`.
- Record successful loads and maintenance cleanup in `social_dw.etl_runs`.
- Run warehouse quality validation before exports are used for Power BI or screenshots.

Canonical production run:

```powershell
python -m etl.cli run --sources youtube --channel-ids $env:YOUTUBE_CHANNEL_IDS --queries= --limit 50 --comments-limit 100 --max-search-pages 12 --database-url $env:DATABASE_URL
python -m etl.cli quality --database-url $env:DATABASE_URL
python -m etl.cli export --database-url $env:DATABASE_URL
```

## API Contract

Required endpoints:

- `GET /health/`
- `GET /api/v1/posts/`
- `GET /api/v1/posts/{post_id}/`
- `GET /api/v1/analytics/overview/`
- `GET /api/v1/analytics/engagement/`
- `GET /api/v1/analytics/sentiment/`
- `GET /api/v1/analytics/top-posts/`
- `GET /api/v1/analytics/content-performance/`
- `GET /api/v1/analytics/heatmap/`
- `GET /api/v1/analytics/competitors/`
- `GET /api/v1/analytics/insights/`
- `GET /api/v1/sync/status/`

API requirements:

- Return JSON with warehouse-backed data.
- Sanitize warehouse errors to `{detail, source_type, error_code}`.
- Keep internal exception details in server logs only.
- Support bounded `limit` parameters on time series and post endpoints.

## Frontend Contract

The Next.js dashboard must:

- Use PostgreSQL-backed Django API data only.
- Avoid runtime imports from `frontend/src/data/*.json`.
- Provide pages for dashboard, content, sentiment, competitors, posts, and data health.
- Provide loading and error states.
- Support English/Vietnamese labels through the local i18n dictionary.

## Validation Contract

Required final checks:

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

Current expected quality gate:

- 43 validation rows.
- 26 PASS.
- 17 INFO.
- 0 FAIL.

The validation SQL must check:

- Duplicate natural keys.
- Orphan facts.
- Non-negative metrics.
- Generated KPI reconciliation.
- Valid sentiment labels and scores.
- YouTube-only platform scope.
- Approved official-channel page scope.

## Final Artifact Contract

Required handoff artifacts:

- `README.md`
- `STATUS.md`
- `GUIDE.md`
- `docs/BI_Insights.md`
- `docs/SQL_Validation_Result.md`
- `docs/Final_Checklist.md`
- `dashboard/exports/*`
- `dashboard/power_bi/README.md`
- Final Power BI `.pbix` created manually in Power BI Desktop.
- Refreshed screenshots after final warehouse/export refresh.
