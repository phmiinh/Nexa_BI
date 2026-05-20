# Power BI Dashboard Guide

Power BI is the primary BI dashboard deliverable for SocialLens BI.

## Data Source

Preferred source:

- PostgreSQL database: `sociallens_bi`
- Schema: `social_dw`
- Views:
  - `vw_executive_overview`
  - `vw_daily_engagement`
  - `vw_sentiment_trend`
  - `vw_content_performance`
  - `vw_competitor_benchmark`
  - `vw_posting_time_heatmap`
  - `vw_viral_posts`

Fallback source:

- CSV exports from `dashboard/exports/`
- Processed ETL CSVs from `data/processed/`

## Pages

1. Executive Overview
   - KPI cards: total reach, total engagement, average engagement rate, sentiment ratio.
   - Trend: daily engagement and reach.

2. Content Performance
   - Top posts.
   - Content type comparison.
   - Reach vs engagement scatter.

3. Sentiment Analysis
   - Positive/neutral/negative trend.
   - Sentiment by platform and brand.

4. Competitor Benchmarking
   - Highlands Coffee vs Phuc Long vs The Coffee House.
   - Share of voice and engagement comparison.

## Validation

Before screenshots or submission:

- Refresh data successfully.
- Confirm slicers for date, platform, brand, content type.
- Compare total engagement, sentiment ratio, and top content with SQL outputs.
