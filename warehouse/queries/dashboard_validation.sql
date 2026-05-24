SET search_path TO social_dw;

WITH table_row_counts AS (
    SELECT 'dim_time' AS object_name, count(*)::bigint AS row_count FROM dim_time
    UNION ALL SELECT 'dim_platform', count(*)::bigint FROM dim_platform
    UNION ALL SELECT 'dim_content_type', count(*)::bigint FROM dim_content_type
    UNION ALL SELECT 'dim_page', count(*)::bigint FROM dim_page
    UNION ALL SELECT 'fact_post', count(*)::bigint FROM fact_post
    UNION ALL SELECT 'fact_sentiment', count(*)::bigint FROM fact_sentiment
),
view_row_counts AS (
    SELECT 'vw_post_performance' AS object_name, count(*)::bigint AS row_count FROM vw_post_performance
    UNION ALL SELECT 'vw_sentiment_daily', count(*)::bigint FROM vw_sentiment_daily
    UNION ALL SELECT 'vw_platform_content_summary', count(*)::bigint FROM vw_platform_content_summary
    UNION ALL SELECT 'vw_best_posting_heatmap', count(*)::bigint FROM vw_best_posting_heatmap
    UNION ALL SELECT 'vw_executive_overview', count(*)::bigint FROM vw_executive_overview
    UNION ALL SELECT 'vw_daily_engagement', count(*)::bigint FROM vw_daily_engagement
    UNION ALL SELECT 'vw_sentiment_trend', count(*)::bigint FROM vw_sentiment_trend
    UNION ALL SELECT 'vw_content_performance', count(*)::bigint FROM vw_content_performance
    UNION ALL SELECT 'vw_competitor_benchmark', count(*)::bigint FROM vw_competitor_benchmark
    UNION ALL SELECT 'vw_posting_time_heatmap', count(*)::bigint FROM vw_posting_time_heatmap
    UNION ALL SELECT 'vw_viral_posts', count(*)::bigint FROM vw_viral_posts
),
duplicate_checks AS (
    SELECT 'dim_platform.platform_name' AS check_name, count(*)::bigint AS issue_count
    FROM (
        SELECT platform_name
        FROM dim_platform
        GROUP BY platform_name
        HAVING count(*) > 1
    ) d
    UNION ALL
    SELECT 'dim_content_type.type_name', count(*)::bigint
    FROM (
        SELECT type_name
        FROM dim_content_type
        GROUP BY type_name
        HAVING count(*) > 1
    ) d
    UNION ALL
    SELECT 'dim_page.platform_id + external_page_id', count(*)::bigint
    FROM (
        SELECT platform_id, external_page_id
        FROM dim_page
        WHERE external_page_id IS NOT NULL
        GROUP BY platform_id, external_page_id
        HAVING count(*) > 1
    ) d
    UNION ALL
    SELECT 'dim_page.platform_id + page_name', count(*)::bigint
    FROM (
        SELECT platform_id, page_name
        FROM dim_page
        GROUP BY platform_id, page_name
        HAVING count(*) > 1
    ) d
    UNION ALL
    SELECT 'fact_post.platform_id + external_post_id', count(*)::bigint
    FROM (
        SELECT platform_id, external_post_id
        FROM fact_post
        GROUP BY platform_id, external_post_id
        HAVING count(*) > 1
    ) d
    UNION ALL
    SELECT 'fact_sentiment.platform_id + external_comment_id', count(*)::bigint
    FROM (
        SELECT platform_id, external_comment_id
        FROM fact_sentiment
        GROUP BY platform_id, external_comment_id
        HAVING count(*) > 1
    ) d
),
orphan_checks AS (
    SELECT 'fact_post.time_id -> dim_time' AS check_name, count(*)::bigint AS issue_count
    FROM fact_post fp
    LEFT JOIN dim_time dt ON dt.time_id = fp.time_id
    WHERE dt.time_id IS NULL
    UNION ALL
    SELECT 'fact_post.platform_id -> dim_platform', count(*)::bigint
    FROM fact_post fp
    LEFT JOIN dim_platform dp ON dp.platform_id = fp.platform_id
    WHERE dp.platform_id IS NULL
    UNION ALL
    SELECT 'fact_post.content_type_id -> dim_content_type', count(*)::bigint
    FROM fact_post fp
    LEFT JOIN dim_content_type dct ON dct.content_type_id = fp.content_type_id
    WHERE dct.content_type_id IS NULL
    UNION ALL
    SELECT 'fact_post.page_id -> dim_page', count(*)::bigint
    FROM fact_post fp
    LEFT JOIN dim_page dpg ON dpg.page_id = fp.page_id
    WHERE dpg.page_id IS NULL
    UNION ALL
    SELECT 'fact_sentiment.post_id -> fact_post', count(*)::bigint
    FROM fact_sentiment fs
    LEFT JOIN fact_post fp ON fp.post_id = fs.post_id
    WHERE fp.post_id IS NULL
    UNION ALL
    SELECT 'fact_sentiment.platform_id -> dim_platform', count(*)::bigint
    FROM fact_sentiment fs
    LEFT JOIN dim_platform dp ON dp.platform_id = fs.platform_id
    WHERE dp.platform_id IS NULL
    UNION ALL
    SELECT 'fact_sentiment.time_id -> dim_time', count(*)::bigint
    FROM fact_sentiment fs
    LEFT JOIN dim_time dt ON dt.time_id = fs.time_id
    WHERE dt.time_id IS NULL
    UNION ALL
    SELECT 'fact_sentiment.platform_id matches parent fact_post', count(*)::bigint
    FROM fact_sentiment fs
    JOIN fact_post fp ON fp.post_id = fs.post_id
    WHERE fs.platform_id <> fp.platform_id
),
metric_domain_checks AS (
    SELECT 'fact_post non-negative base metrics' AS check_name, count(*)::bigint AS issue_count
    FROM fact_post
    WHERE hashtag_count < 0
       OR reach < 0
       OR impressions < 0
       OR likes < 0
       OR comments < 0
       OR shares < 0
       OR saves < 0
       OR engagement_count < 0
       OR engagement_rate < 0
       OR virality_score < 0
    UNION ALL
    SELECT 'dim_page non-negative follower_count', count(*)::bigint
    FROM dim_page
    WHERE follower_count < 0
    UNION ALL
    SELECT 'fact_post generated engagement_count matches components', count(*)::bigint
    FROM fact_post
    WHERE engagement_count <> likes + comments + shares + saves
    UNION ALL
    SELECT 'fact_post generated engagement_rate matches components', count(*)::bigint
    FROM fact_post
    WHERE engagement_rate IS DISTINCT FROM
        CASE WHEN reach > 0 THEN round(((likes + comments + shares + saves)::numeric / reach::numeric) * 100, 4) ELSE NULL END
    UNION ALL
    SELECT 'fact_post generated virality_score matches components', count(*)::bigint
    FROM fact_post
    WHERE virality_score IS DISTINCT FROM
        CASE WHEN reach > 0 THEN round((shares::numeric / reach::numeric) * 100, 4) ELSE NULL END
),
sentiment_domain_checks AS (
    SELECT 'fact_sentiment valid sentiment_label' AS check_name, count(*)::bigint AS issue_count
    FROM fact_sentiment
    WHERE sentiment_label NOT IN ('positive', 'neutral', 'negative')
    UNION ALL
    SELECT 'fact_sentiment sentiment_score between -1 and 1', count(*)::bigint
    FROM fact_sentiment
    WHERE sentiment_score < -1 OR sentiment_score > 1
),
base_kpis AS (
    SELECT
        count(*)::bigint AS total_posts,
        sum(reach)::bigint AS total_reach,
        sum(impressions)::bigint AS total_impressions,
        sum(engagement_count)::bigint AS total_engagement,
        round(avg(engagement_rate), 4) AS avg_engagement_rate,
        round(avg(virality_score), 4) AS avg_virality_score,
        min(dt.full_date) AS date_from,
        max(dt.full_date) AS date_to
    FROM fact_post fp
    JOIN dim_time dt ON dt.time_id = fp.time_id
),
view_kpis AS (
    SELECT
        total_posts,
        total_reach,
        total_impressions,
        total_engagement,
        avg_engagement_rate,
        avg_virality_score,
        date_from,
        date_to
    FROM vw_executive_overview
),
dashboard_30d_direct AS (
    SELECT
        count(*)::bigint AS total_posts,
        sum(reach)::bigint AS total_reach,
        sum(impressions)::bigint AS total_impressions,
        sum(engagement_count)::bigint AS total_engagement,
        round(avg(engagement_rate), 4) AS avg_engagement_rate,
        round(avg(virality_score), 4) AS avg_virality_score
    FROM vw_post_performance
    WHERE full_date >= CURRENT_DATE - INTERVAL '30 days'
),
dashboard_30d_view_source AS (
    SELECT
        count(*)::bigint AS total_posts,
        sum(reach)::bigint AS total_reach,
        sum(impressions)::bigint AS total_impressions,
        sum(engagement_count)::bigint AS total_engagement,
        round(avg(engagement_rate), 4) AS avg_engagement_rate,
        round(avg(virality_score), 4) AS avg_virality_score
    FROM fact_post fp
    JOIN dim_time dt ON dt.time_id = fp.time_id
    WHERE dt.full_date >= CURRENT_DATE - INTERVAL '30 days'
),
kpi_reconciliation_checks AS (
    SELECT
        'vw_executive_overview reconciles to fact_post' AS check_name,
        CASE
            WHEN bk.total_posts IS DISTINCT FROM vk.total_posts
              OR bk.total_reach IS DISTINCT FROM vk.total_reach
              OR bk.total_impressions IS DISTINCT FROM vk.total_impressions
              OR bk.total_engagement IS DISTINCT FROM vk.total_engagement
              OR bk.avg_engagement_rate IS DISTINCT FROM vk.avg_engagement_rate
              OR bk.avg_virality_score IS DISTINCT FROM vk.avg_virality_score
              OR bk.date_from IS DISTINCT FROM vk.date_from
              OR bk.date_to IS DISTINCT FROM vk.date_to
            THEN 1::bigint ELSE 0::bigint
        END AS issue_count,
        jsonb_build_object('base', to_jsonb(bk), 'view', to_jsonb(vk)) AS details
    FROM base_kpis bk
    CROSS JOIN view_kpis vk
    UNION ALL
    SELECT
        '30-day dashboard KPI query reconciles to fact_post' AS check_name,
        CASE
            WHEN d.total_posts IS DISTINCT FROM s.total_posts
              OR d.total_reach IS DISTINCT FROM s.total_reach
              OR d.total_impressions IS DISTINCT FROM s.total_impressions
              OR d.total_engagement IS DISTINCT FROM s.total_engagement
              OR d.avg_engagement_rate IS DISTINCT FROM s.avg_engagement_rate
              OR d.avg_virality_score IS DISTINCT FROM s.avg_virality_score
            THEN 1::bigint ELSE 0::bigint
        END AS issue_count,
        jsonb_build_object('dashboard_view_query', to_jsonb(d), 'fact_source_query', to_jsonb(s)) AS details
    FROM dashboard_30d_direct d
    CROSS JOIN dashboard_30d_view_source s
),
youtube_scope_checks AS (
    SELECT
        'fact_post platform data is YouTube-only' AS check_name,
        count(*)::bigint AS issue_count,
        jsonb_build_object(
            'non_youtube_rows', count(*),
            'platforms_present', coalesce(jsonb_agg(DISTINCT dp.platform_name) FILTER (WHERE dp.platform_name <> 'youtube'), '[]'::jsonb)
        ) AS details
    FROM fact_post fp
    JOIN dim_platform dp ON dp.platform_id = fp.platform_id
    WHERE dp.platform_name <> 'youtube'
    UNION ALL
    SELECT
        'fact_sentiment platform data is YouTube-only',
        count(*)::bigint,
        jsonb_build_object(
            'non_youtube_rows', count(*),
            'platforms_present', coalesce(jsonb_agg(DISTINCT dp.platform_name) FILTER (WHERE dp.platform_name <> 'youtube'), '[]'::jsonb)
        )
    FROM fact_sentiment fs
    JOIN dim_platform dp ON dp.platform_id = fs.platform_id
    WHERE dp.platform_name <> 'youtube'
)
SELECT
    (now() AT TIME ZONE 'Asia/Ho_Chi_Minh')::timestamp(0) AS validated_at_vn,
    'row_count' AS check_group,
    object_name AS check_name,
    'INFO' AS status,
    row_count AS observed_value,
    jsonb_build_object('row_count', row_count) AS details
FROM table_row_counts
UNION ALL
SELECT
    (now() AT TIME ZONE 'Asia/Ho_Chi_Minh')::timestamp(0),
    'view_row_count',
    object_name,
    'INFO',
    row_count,
    jsonb_build_object('row_count', row_count)
FROM view_row_counts
UNION ALL
SELECT
    (now() AT TIME ZONE 'Asia/Ho_Chi_Minh')::timestamp(0),
    'duplicate_natural_key',
    check_name,
    CASE WHEN issue_count = 0 THEN 'PASS' ELSE 'FAIL' END,
    issue_count,
    jsonb_build_object('duplicate_groups', issue_count)
FROM duplicate_checks
UNION ALL
SELECT
    (now() AT TIME ZONE 'Asia/Ho_Chi_Minh')::timestamp(0),
    'orphan_fact_check',
    check_name,
    CASE WHEN issue_count = 0 THEN 'PASS' ELSE 'FAIL' END,
    issue_count,
    jsonb_build_object('orphan_rows', issue_count)
FROM orphan_checks
UNION ALL
SELECT
    (now() AT TIME ZONE 'Asia/Ho_Chi_Minh')::timestamp(0),
    'non_negative_metric',
    check_name,
    CASE WHEN issue_count = 0 THEN 'PASS' ELSE 'FAIL' END,
    issue_count,
    jsonb_build_object('invalid_rows', issue_count)
FROM metric_domain_checks
UNION ALL
SELECT
    (now() AT TIME ZONE 'Asia/Ho_Chi_Minh')::timestamp(0),
    'sentiment_validity',
    check_name,
    CASE WHEN issue_count = 0 THEN 'PASS' ELSE 'FAIL' END,
    issue_count,
    jsonb_build_object('invalid_rows', issue_count)
FROM sentiment_domain_checks
UNION ALL
SELECT
    (now() AT TIME ZONE 'Asia/Ho_Chi_Minh')::timestamp(0),
    'dashboard_kpi_reconciliation',
    check_name,
    CASE WHEN issue_count = 0 THEN 'PASS' ELSE 'FAIL' END,
    issue_count,
    details
FROM kpi_reconciliation_checks
UNION ALL
SELECT
    (now() AT TIME ZONE 'Asia/Ho_Chi_Minh')::timestamp(0),
    'platform_scope',
    check_name,
    CASE WHEN issue_count = 0 THEN 'PASS' ELSE 'FAIL' END,
    issue_count,
    details
FROM youtube_scope_checks
ORDER BY check_group, check_name;
