# SocialLens BI SQL Validation Result

Validated warehouse: `social_dw` on database `nexabi`
Validated at: `2026-06-01` Asia/Ho_Chi_Minh
Validation SQL: `warehouse/queries/dashboard_validation.sql`

## Execution

Validation was executed through:

```powershell
python -m etl.cli quality --database-url $env:DATABASE_URL
```

Command result: `43` validation rows: `26 PASS`, `17 INFO`, `0 FAIL`.

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
| Approved official-channel scope | PASS |

No validation blocker remains.

## Row Counts

| Object | Rows |
| --- | ---: |
| `dim_page` | 8 |
| `fact_post` | 817 |
| `fact_sentiment` | 1,526 |
| `vw_post_performance` | 817 |
| `vw_sentiment_trend` | 926 |
| `vw_daily_engagement` | 568 |
| `vw_competitor_benchmark` | 8 |
| `vw_posting_time_heatmap` | 122 |
| `vw_executive_overview` | 1 |

## Dashboard KPI Reconciliation

`vw_executive_overview` reconciles to the fact source.

| KPI | View |
| --- | ---: |
| `total_posts` | 817 |
| `total_reach` | 167,066,949 |
| `total_impressions` | 167,066,949 |
| `total_engagement` | 48,325 |
| `avg_engagement_rate` | 1.9164 |
| `avg_virality_score` | 0.0000 |
| `date_from` | 2017-09-26 |
| `date_to` | 2026-05-26 |

Status: PASS.

## Quality Checks

| Check | Status | Observed |
| --- | --- | ---: |
| Duplicate post natural keys | PASS | 0 |
| Duplicate comment natural keys | PASS | 0 |
| Orphan sentiments | PASS | 0 |
| Invalid sentiment labels | PASS | 0 |
| Sentiment scores outside [-1, 1] | PASS | 0 |
| Non-YouTube fact rows | PASS | 0 |
| Non-approved official channel fact rows | PASS | 0 |

## Official-Only Cleanup

On 2026-06-01, the warehouse was reconciled to the accepted official-channel batch from `data/processed`:

| Cleanup item | Count |
| --- | ---: |
| Removed lower-confidence query residual posts | 59 |
| Removed comments attached to those posts | 166 |
| Removed orphan pages | 41 |
| Retained official-channel posts | 817 |
| Retained official-channel comments | 1,526 |

The removed rows were archived under `data/processed_archive/`.

## Re-run Command

```powershell
Get-Content .env | Where-Object { $_ -match '^[A-Za-z_][A-Za-z0-9_]*=' } | ForEach-Object {
  $name, $value = $_ -split '=', 2
  Set-Item -Path "Env:$name" -Value $value
}
python -m etl.cli quality --database-url $env:DATABASE_URL
python -m etl.cli export --database-url $env:DATABASE_URL
```
