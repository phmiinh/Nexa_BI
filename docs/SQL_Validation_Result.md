# SocialLens BI SQL Validation Result

Validated warehouse: `social_dw` on database `nexabi`
Validated at: `2026-05-24 16:08:29` Asia/Ho_Chi_Minh
Validation SQL: `warehouse/queries/dashboard_validation.sql`

## Execution

`psql` is not required for the current Windows workflow. Validation was executed with Python `psycopg` using `.env` database credentials.

Command result: `42` validation rows, `0` failures.

## Summary

| Area | Result |
| --- | --- |
| Row counts | PASS |
| Duplicate natural keys | PASS |
| Orphan fact checks | PASS |
| Non-negative metrics and generated formulas | PASS |
| Sentiment label and score validity | PASS |
| Dashboard KPI reconciliation | PASS |
| YouTube-only platform scope | PASS |

No validation blocker remains.

## Row Counts

| Object | Rows |
| --- | ---: |
| `dim_content_type` | 8 |
| `dim_page` | 11 |
| `dim_platform` | 4 |
| `dim_time` | 80 |
| `fact_post` | 65 |
| `fact_sentiment` | 15 |
| `vw_best_posting_heatmap` | 46 |
| `vw_competitor_benchmark` | 11 |
| `vw_content_performance` | 2 |
| `vw_daily_engagement` | 43 |
| `vw_executive_overview` | 1 |
| `vw_platform_content_summary` | 2 |
| `vw_post_performance` | 65 |
| `vw_posting_time_heatmap` | 46 |
| `vw_sentiment_daily` | 13 |
| `vw_sentiment_trend` | 13 |
| `vw_viral_posts` | 65 |

## Dashboard KPI Reconciliation

`vw_executive_overview` reconciles exactly to the fact source.

| KPI | Fact Source | View |
| --- | ---: | ---: |
| `total_posts` | 65 | 65 |
| `total_reach` | 6237370 | 6237370 |
| `total_impressions` | 6237370 | 6237370 |
| `total_engagement` | 1151 | 1151 |
| `avg_engagement_rate` | 0.7435 | 0.7435 |
| `avg_virality_score` | 0.0 | 0.0 |
| `date_from` | 2023-01-01 | 2023-01-01 |
| `date_to` | 2026-05-19 | 2026-05-19 |

Status: PASS.

### 30-Day Dashboard KPI

| KPI | Dashboard View Query | Fact Source Query |
| --- | ---: | ---: |
| `total_posts` | 6 | 6 |
| `total_reach` | 2346 | 2346 |
| `total_impressions` | 2346 | 2346 |
| `total_engagement` | 16 | 16 |
| `avg_engagement_rate` | 0.9376 | 0.9376 |
| `avg_virality_score` | 0.0 | 0.0 |

Status: PASS.

## Quality Checks

### Duplicate Natural Key

| Check | Status | Observed |
| --- | --- | ---: |
| `dim_content_type.type_name` | PASS | 0 |
| `dim_page.platform_id + external_page_id` | PASS | 0 |
| `dim_page.platform_id + page_name` | PASS | 0 |
| `dim_platform.platform_name` | PASS | 0 |
| `fact_post.platform_id + external_post_id` | PASS | 0 |
| `fact_sentiment.platform_id + external_comment_id` | PASS | 0 |

### Orphan Fact Check

| Check | Status | Observed |
| --- | --- | ---: |
| `fact_post.content_type_id -> dim_content_type` | PASS | 0 |
| `fact_post.page_id -> dim_page` | PASS | 0 |
| `fact_post.platform_id -> dim_platform` | PASS | 0 |
| `fact_post.time_id -> dim_time` | PASS | 0 |
| `fact_sentiment.platform_id -> dim_platform` | PASS | 0 |
| `fact_sentiment.platform_id matches parent fact_post` | PASS | 0 |
| `fact_sentiment.post_id -> fact_post` | PASS | 0 |
| `fact_sentiment.time_id -> dim_time` | PASS | 0 |

### Non Negative Metric

| Check | Status | Observed |
| --- | --- | ---: |
| `dim_page non-negative follower_count` | PASS | 0 |
| `fact_post generated engagement_count matches components` | PASS | 0 |
| `fact_post generated engagement_rate matches components` | PASS | 0 |
| `fact_post generated virality_score matches components` | PASS | 0 |
| `fact_post non-negative base metrics` | PASS | 0 |

### Sentiment Validity

| Check | Status | Observed |
| --- | --- | ---: |
| `fact_sentiment sentiment_score between -1 and 1` | PASS | 0 |
| `fact_sentiment valid sentiment_label` | PASS | 0 |

### Platform Scope

| Check | Status | Observed |
| --- | --- | ---: |
| `fact_post platform data is YouTube-only` | PASS | 0 |
| `fact_sentiment platform data is YouTube-only` | PASS | 0 |

## Re-run Command

```powershell
Get-Content .env | Where-Object { $_ -match '^[A-Za-z_][A-Za-z0-9_]*=' } | ForEach-Object { $name, $value = $_ -split '=', 2; Set-Item -Path "Env:$name" -Value $value }
python - <<'PY'
# Use the Python psycopg runner documented in this file or run the SQL in warehouse/queries/dashboard_validation.sql with psql.
PY
```
