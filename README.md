# SocialLens BI

<p align="center">
  <strong>Business Intelligence system for F&amp;B social media analytics</strong><br>
  Highlands Coffee Vietnam vs. selected competitors on official YouTube channels
</p>

<p align="center">
  <a href="./Report%20Business%20Intelligence.pdf">
    <img alt="Final report" src="https://img.shields.io/badge/Final_Report-PDF-B31B1B?style=for-the-badge&logo=adobeacrobatreader&logoColor=white">
  </a>
  <a href="https://github.com/phmiinh/Nexa_BI">
    <img alt="Repository" src="https://img.shields.io/badge/GitHub-Nexa_BI-181717?style=for-the-badge&logo=github&logoColor=white">
  </a>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-ETL-3776AB?style=flat-square&logo=python&logoColor=white">
  <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-Warehouse-4169E1?style=flat-square&logo=postgresql&logoColor=white">
  <img alt="Django" src="https://img.shields.io/badge/Django-API-092E20?style=flat-square&logo=django&logoColor=white">
  <img alt="Next.js" src="https://img.shields.io/badge/Next.js-Dashboard-000000?style=flat-square&logo=nextdotjs&logoColor=white">
  <img alt="TypeScript" src="https://img.shields.io/badge/TypeScript-Frontend-3178C6?style=flat-square&logo=typescript&logoColor=white">
  <img alt="YouTube" src="https://img.shields.io/badge/YouTube-Data_API-FF0000?style=flat-square&logo=youtube&logoColor=white">
</p>

## Final Report

The full submission report is available here:

**[Open Report Business Intelligence.pdf](./Report%20Business%20Intelligence.pdf)**

The PDF contains the final written report, dashboard screenshots, data warehouse explanation, validation summary, and BI insights.

## What This Project Does

SocialLens BI turns real YouTube data from official F&B brand channels into a structured BI workflow. The project extracts video and comment data, cleans and models it into a PostgreSQL warehouse, exposes analytical views through a Django API, and presents the result in a Next.js dashboard.

The final scope is intentionally focused on **official YouTube channels**. Broad query-search data was excluded because it introduced non-official pages and distorted reach-based benchmarking. The final submission prioritizes clean, explainable, and validated data over raw volume.

## Final Data Snapshot

| Metric | Final value |
| --- | ---: |
| Official YouTube pages | 8 |
| Fact posts | 817 |
| Sentiment-classified comments | 1,526 |
| Date range | 2017-09-26 to 2026-05-26 |
| Total reach/views proxy | 167,066,949 |
| Total engagement | 48,325 |
| Average engagement rate | 1.9164% |
| Warehouse quality gate | 26 PASS, 17 INFO, 0 FAIL |

`reach` is a YouTube views/impressions proxy, not unique reach. `virality_score` is defined in the model but remains 0 in the final snapshot because YouTube Data API v3 does not expose share count through this pipeline.

## BI Questions

The project is built around three practical business questions:

1. Which content performs best for Highlands Coffee and competing F&B brands?
2. How are audiences responding through comment sentiment?
3. Where does Highlands stand against competitors in reach, engagement, engagement rate, and share of voice?

## Main Findings

Highlands Coffee dominates reach in the official YouTube dataset, accounting for **96.24% reach-based share of voice**. That does not mean Highlands is the strongest brand on every metric: Trung Nguyên Legend leads in posting cadence, engagement volume, and comment coverage with **600/817 posts** and **1,258/1,526 comments**.

The most useful contrast in the project is therefore not "who has the most views", but how awareness and engagement tell different stories. Highlands is strong in reach; Trung Nguyên Legend is the stronger benchmark for consistent content activity and discussion.

Sentiment is broadly safe, with low negative volume, but it is not strongly positive. Most comments are neutral, which matters in F&B because beverage content should ideally trigger appetite, routine, store experience, memory, or personal moments rather than only informational reactions.

## System Flow

```text
YouTube Data API v3
        |
        v
Python ETL
extract -> raw JSONL -> normalize -> sentiment -> quality -> load
        |
        v
PostgreSQL warehouse: social_dw
        |
        +--> Analytical views -> CSV/JSON exports
        |
        +--> Django API -> Next.js dashboard
```

The dashboard reads from the API and warehouse. It does not use static mock JSON as a runtime fallback.

## Warehouse Model

The warehouse uses a star schema to keep BI queries simple and explainable.

| Layer | Objects |
| --- | --- |
| Dimensions | `dim_time`, `dim_platform`, `dim_content_type`, `dim_page` |
| Facts | `fact_post`, `fact_sentiment` |
| Audit | `etl_runs` |
| Analytical views | `vw_executive_overview`, `vw_daily_engagement`, `vw_sentiment_trend`, `vw_content_performance`, `vw_competitor_benchmark`, `vw_posting_time_heatmap`, `vw_viral_posts` |

## Run Locally

Create `.env` from `.env.example`, then set the database URL and YouTube API values:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/nexabi
SOCIALENS_DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/nexabi
YOUTUBE_API_KEY=...
YOUTUBE_CHANNEL_IDS=...
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt

cd frontend
npm install
cd ..
```

Run the API:

```powershell
python backend\manage.py runserver 127.0.0.1:8000
```

Run the dashboard:

```powershell
cd frontend
$env:NEXT_PUBLIC_API_BASE_URL="http://localhost:8000"
npm run dev
```

Open:

```text
http://localhost:3000/dashboard
```

## ETL And Validation

Run official-channel ETL when YouTube API key/quota is available:

```powershell
python -m etl.cli run --sources youtube --channel-ids $env:YOUTUBE_CHANNEL_IDS --queries= --limit 50 --comments-limit 100 --max-search-pages 12 --database-url $env:DATABASE_URL
```

Validate and export:

```powershell
python -m etl.cli quality --database-url $env:DATABASE_URL
python -m etl.cli export --database-url $env:DATABASE_URL
```

Final verification results:

| Check | Result |
| --- | --- |
| Python regression tests | 59 passed, 1 skipped |
| Python coverage | 70.59% |
| Django check | Pass |
| Frontend tests | 7 passed |
| Frontend lint/build | Pass |
| Production npm audit | 0 vulnerabilities |
| Warehouse quality | 26 PASS, 17 INFO, 0 FAIL |

## Repository Map

```text
backend/                 Django API
etl/                     Python ETL package and CLI
warehouse/               PostgreSQL schema, indexes, views, validation SQL
frontend/                Next.js dashboard
dashboard/exports/       CSV/JSON exports from final analytical views
data/processed/          Processed post/comment snapshots
tests/                   Regression and contract tests
```

## Scope Notes

The final report represents official YouTube channel performance only. It does not claim to measure the entire social media footprint of the F&B market. Facebook, TikTok, Instagram, earned media, KOL content, and private YouTube Analytics metrics remain outside the current scope.

The Coffee House is not included in the final clean warehouse because a reliable official YouTube channel ID was not verified. Sentiment analysis is rule-based and should be read as a directional signal rather than a manually validated NLP benchmark.

## License

Academic project for Business Intelligence coursework.
