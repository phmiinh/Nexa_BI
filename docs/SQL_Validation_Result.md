# SocialLens BI SQL Validation Result

Validated warehouse: `social_dw` on database `nexabi`
Validated at: `2026-05-31` Asia/Ho_Chi_Minh
Validation SQL: `warehouse/queries/dashboard_validation.sql`

## Execution

Validation was executed through:

```powershell
python -m etl.cli quality --database-url $env:DATABASE_URL
```

Command result: `42` validation rows: `25 PASS`, `17 INFO`, `0 FAIL`.

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
| `dim_page` | 49 |
| `fact_post` | 876 |
| `fact_sentiment` | 1,692 |
| `vw_post_performance` | 876 |
| `vw_sentiment_trend` | 968 |
| `vw_executive_overview` | 1 |

## Dashboard KPI Reconciliation

`vw_executive_overview` reconciles to the fact source.

| KPI | View |
| --- | ---: |
| `total_posts` | 876 |
| `total_reach` | 167,400,096 |
| `total_impressions` | 167,400,096 |
| `total_engagement` | 53,845 |
| `avg_engagement_rate` | 1.8806 |
| `avg_virality_score` | 0.0000 |
| `date_from` | 2017-09-26 |
| `date_to` | 2026-05-31 |

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

## Re-run Command

```powershell
Get-Content .env | Where-Object { $_ -match '^[A-Za-z_][A-Za-z0-9_]*=' } | ForEach-Object {
  $name, $value = $_ -split '=', 2
  Set-Item -Path "Env:$name" -Value $value
}
python -m etl.cli quality --database-url $env:DATABASE_URL
python -m etl.cli export --database-url $env:DATABASE_URL
```
