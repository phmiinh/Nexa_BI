# SocialLens BI ETL Process

## Load Order

1. Create warehouse objects.

```bash
psql "$DATABASE_URL" -f warehouse/schema/001_schema.sql
psql "$DATABASE_URL" -f warehouse/schema/002_indexes.sql
psql "$DATABASE_URL" -f warehouse/schema/003_views.sql
```

2. Load dimensions.

- Upsert `dim_platform` and `dim_content_type`; default values are seeded by `001_schema.sql`.
- Generate `dim_time` for every post publish timestamp and comment timestamp.
- Upsert `dim_page` by `(platform_id, external_page_id)` when source ids exist, otherwise by `(platform_id, page_name)`.

3. Load facts.

- Upsert `fact_post` by `(platform_id, external_post_id)`.
- Upsert `fact_sentiment` by `(platform_id, external_comment_id)` after resolving `post_id`.

## Transform Rules

| Field | Rule |
| --- | --- |
| Timestamps | Convert source timestamps to reporting timezone before deriving `dim_time`; store exact timestamp in `full_timestamp`. |
| Platform | Lowercase and map to seeded values: `facebook`, `instagram`, `tiktok`, `youtube`. |
| Content type | Lowercase and map to `dim_content_type`; unknown formats should be reviewed before insert. |
| Metrics | Missing counts become 0 only when source field is absent and the API semantics allow it. |
| Engagement rate | Do not load directly; PostgreSQL generates it from reach and engagement counts. |
| Sentiment label | Must be one of `positive`, `neutral`, `negative`. |
| Sentiment score | Clamp or reject values outside -1.0 to 1.0. |

## Example Time Dimension Insert

```sql
INSERT INTO social_dw.dim_time (
    time_id,
    full_date,
    full_timestamp,
    hour_of_day,
    day_of_week,
    day_name,
    week_of_year,
    month_of_year,
    month_name,
    quarter_of_year,
    calendar_year,
    is_weekend
)
SELECT
    to_char(ts, 'YYYYMMDDHH24')::integer,
    ts::date,
    ts,
    extract(hour from ts)::smallint,
    extract(isodow from ts)::smallint,
    to_char(ts, 'FMDay'),
    extract(week from ts)::smallint,
    extract(month from ts)::smallint,
    to_char(ts, 'FMMonth'),
    extract(quarter from ts)::smallint,
    extract(year from ts)::smallint,
    extract(isodow from ts) IN (6, 7)
FROM (VALUES ('2026-05-20 09:00:00+07'::timestamptz)) AS v(ts)
ON CONFLICT (time_id) DO NOTHING;
```

## Query Layer

Use files in `warehouse/queries/` for Power BI datasets or ad hoc analysis:

- `executive_overview.sql`
- `engagement_analysis.sql`
- `sentiment_trend.sql`
- `content_performance.sql`
- `competitor_benchmark.sql`
- `heatmap_posting_time.sql`
- `viral_posts.sql`
