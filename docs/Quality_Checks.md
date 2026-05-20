# SocialLens BI Quality Checks

Run these checks after each load.

## Referential Integrity

```sql
SELECT count(*) AS orphan_posts
FROM social_dw.fact_post fp
LEFT JOIN social_dw.dim_time dt ON dt.time_id = fp.time_id
LEFT JOIN social_dw.dim_platform dp ON dp.platform_id = fp.platform_id
LEFT JOIN social_dw.dim_content_type dct ON dct.content_type_id = fp.content_type_id
LEFT JOIN social_dw.dim_page dpg ON dpg.page_id = fp.page_id
WHERE dt.time_id IS NULL
   OR dp.platform_id IS NULL
   OR dct.content_type_id IS NULL
   OR dpg.page_id IS NULL;
```

```sql
SELECT count(*) AS orphan_sentiments
FROM social_dw.fact_sentiment fs
LEFT JOIN social_dw.fact_post fp ON fp.post_id = fs.post_id
LEFT JOIN social_dw.dim_time dt ON dt.time_id = fs.time_id
WHERE fp.post_id IS NULL
   OR dt.time_id IS NULL;
```

## Metric Validity

```sql
SELECT count(*) AS invalid_post_metrics
FROM social_dw.fact_post
WHERE reach < 0
   OR impressions < 0
   OR likes < 0
   OR comments < 0
   OR shares < 0
   OR saves < 0
   OR engagement_rate < 0
   OR virality_score < 0;
```

```sql
SELECT count(*) AS invalid_sentiment_scores
FROM social_dw.fact_sentiment
WHERE sentiment_score < -1
   OR sentiment_score > 1
   OR sentiment_label NOT IN ('positive', 'neutral', 'negative');
```

## Duplicate Source Records

```sql
SELECT platform_id, external_post_id, count(*)
FROM social_dw.fact_post
GROUP BY platform_id, external_post_id
HAVING count(*) > 1;
```

```sql
SELECT platform_id, external_comment_id, count(*)
FROM social_dw.fact_sentiment
GROUP BY platform_id, external_comment_id
HAVING count(*) > 1;
```

## Dashboard Readiness

```sql
SELECT 'vw_post_performance' AS object_name, count(*) AS row_count
FROM social_dw.vw_post_performance
UNION ALL
SELECT 'vw_sentiment_daily', count(*)
FROM social_dw.vw_sentiment_daily
UNION ALL
SELECT 'vw_best_posting_heatmap', count(*)
FROM social_dw.vw_best_posting_heatmap;
```
