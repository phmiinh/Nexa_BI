# SocialLens BI Specification

## 1. Project Intent

SocialLens BI is a Business Intelligence capstone project for analyzing social media performance for an F&B brand. The project follows `README.md` and `ROADMAP.md` as the business scope. `DESIGN.md` is used only as technical guidance for Python, Django, Next.js, PostgreSQL, and dashboard implementation.

This file is the implementation source of truth. Any intentional change to scope, architecture, schema, API, dashboard, tests, or deliverables must be recorded in `STATUS.md`.

## 2. Case Study

- Industry: F&B
- Main brand: Highlands Coffee
- Competitors: Phuc Long, The Coffee House
- Primary real platform: YouTube
- Sample mode: YouTube/F&B synthetic data for local development and automated tests only
- Facebook Graph API is not required for the MVP
- Extension platforms: TikTok and Instagram, only if data is available after the MVP works

## 3. Data Strategy

The project uses YouTube real API extraction as the production/demo data source. Sample data remains available for development and automated tests, but the primary `make etl` and `make demo` workflows must run with sample fallback disabled because a real YouTube API key is available.

Extraction priority:

1. YouTube Data API, when `YOUTUBE_API_KEY` and `YOUTUBE_CHANNEL_IDS` or `YOUTUBE_QUERIES` are configured.
2. Deterministic YouTube/F&B sample fallback, available only for local development, tests, and explicit fallback runs.
3. Facebook Graph API is optional and out of MVP scope because of Page permission and App Review risk.

Raw records must be stored as JSONL under `data/raw/{source}/` by `run_id`. Processed outputs must be written under `data/processed/` as CSV files so Power BI can import data even when the database connection is unavailable.

## 4. Business Questions

The BI deliverables must answer these questions:

- Which content performs best by engagement, reach, virality, and sentiment?
- Is customer sentiment positive, neutral, or negative over time?
- What are competitors doing better than the main brand?
- Which posting time, platform, and content type should the brand prioritize?
- How does share of voice change against competitors?

## 5. Canonical KPIs

All notebooks, SQL, API responses, Power BI visuals, and Next.js dashboard widgets must use these definitions:

- `engagement_count = likes + comments + shares + saves`
- `engagement_rate = engagement_count / reach * 100`
- `virality_score = shares / reach * 100`
- `sentiment_ratio = positive_comments / total_comments * 100`
- `reach_growth = (current_reach - previous_reach) / previous_reach * 100`
- `share_of_voice = brand_mentions / total_industry_mentions * 100`

Rules:

- Use `NULL` for rates when the denominator is zero or missing.
- Store timestamps in UTC; dashboard and SQL analysis should present Vietnam time using `Asia/Ho_Chi_Minh`.
- Insights must include one key finding, two or three supporting numbers, a date range, and a recommended action.

## 6. Data Warehouse

Warehouse engine: PostgreSQL 16.

Schema: `social_dw`.

Required star schema:

- `dim_time`
- `dim_platform`
- `dim_content_type`
- `dim_page`
- `fact_post`
- `fact_sentiment`

Fact grains:

- `fact_post`: one row per social media post/video.
- `fact_sentiment`: one row per comment with sentiment.

Required analytical views:

- `vw_executive_overview`
- `vw_daily_engagement`
- `vw_sentiment_trend`
- `vw_content_performance`
- `vw_competitor_benchmark`
- `vw_posting_time_heatmap`
- `vw_viral_posts`

## 7. ETL Requirements

The ETL pipeline must be runnable from the command line and through `make demo`.

Required behavior:

- Extract real YouTube API data when credentials exist.
- Fail production/demo ETL runs when YouTube credentials, channel ids, queries, or API calls fail.
- Fall back to deterministic sample data only when an explicit dev/test fallback run is requested.
- Normalize posts and comments to shared schemas.
- Deduplicate by `(platform, external_id)`.
- Compute KPI fields consistently.
- Run rule-based Vietnamese sentiment fallback without heavy model downloads.
- Upsert into PostgreSQL without duplicating fact rows.
- Record each run in an ETL audit table or a status artifact.
- Export processed CSV files for Power BI.

## 8. Dashboard Requirements

Power BI is the primary BI deliverable. Next.js is a web demo/dashboard.

Power BI pages:

- Executive Overview
- Content Performance
- Sentiment Analysis
- Competitor Benchmarking

Next.js pages:

- `/dashboard`
- `/content`
- `/sentiment`
- `/competitors`
- `/posts`
- `/data-health`

Next.js must consume Django API first and use static JSON fallback if API data is unavailable.

## 9. API Requirements

Django API is a read layer over warehouse views and processed data. It must not hold complex BI logic in views.

Minimum endpoints:

- `GET /api/v1/posts/`
- `GET /api/v1/posts/{id}/`
- `GET /api/v1/analytics/overview/`
- `GET /api/v1/analytics/engagement/`
- `GET /api/v1/analytics/sentiment/`
- `GET /api/v1/analytics/top-posts/`
- `GET /api/v1/analytics/content-performance/`
- `GET /api/v1/analytics/heatmap/`
- `GET /api/v1/analytics/competitors/`
- `GET /api/v1/sync/status/`

## 10. Notebooks And Documentation

Required notebooks:

- `01_data_quality_overview.ipynb`
- `02_kpi_baseline.ipynb`
- `03_content_performance_analysis.ipynb`
- `04_posting_time_heatmap.ipynb`
- `05_sentiment_brand_health.ipynb`
- `06_share_of_voice_competitor.ipynb`
- `07_executive_insights.ipynb`

Required docs:

- `docs/Data_Dictionary.md`
- `docs/ETL_Process.md`
- `docs/Quality_Checks.md`
- dashboard screenshots under `dashboard/screenshots/`

## 11. Test And Acceptance Criteria

ETL tests:

- Mock YouTube success, HTTP error, timeout, and pagination.
- Missing credentials fail when `--no-sample-fallback` is enabled.
- Explicit fallback mode uses YouTube/F&B sample data for local tests.
- Normalization handles timestamps, nulls, duplicates, and engagement formulas.
- Load is idempotent.

Data quality:

- No duplicate natural keys.
- No orphan fact rows.
- Metrics are non-negative.
- Sentiment labels and scores are valid.
- Processed row counts reconcile with warehouse row counts.

SQL validation:

- Each dashboard KPI has a validation query.
- Validate row counts, foreign keys, trends, top content, and platform comparison.

Smoke test:

- `make demo` creates schema, runs real YouTube ETL with fallback disabled, runs quality checks, writes processed CSVs, and exports dashboard-ready data.

## 12. Agent Coordination Policy

Agents are used only when their specialist scope is active:

- `orchestrator`: scope and sequencing checks.
- `analyst`: KPI, insights, and BI query meaning.
- `data-engineer`: warehouse schema, SQL, data dictionary.
- `etl-runner`: ETL, API extraction, sentiment, load.
- `api-designer`: Django API contracts.
- `devops`: Docker, environment, Makefile, CI.
- `frontend-builder`: Next.js dashboard.
- `test-writer`: tests and smoke validation.

Do not spawn all agents at once. After each phase, update `STATUS.md`.
