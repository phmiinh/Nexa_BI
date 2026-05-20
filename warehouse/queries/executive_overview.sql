SET search_path TO social_dw;

WITH current_period AS (
    SELECT *
    FROM vw_post_performance
    WHERE full_date >= CURRENT_DATE - INTERVAL '30 days'
),
sentiment AS (
    SELECT
        round(avg(avg_sentiment_score), 4) AS avg_sentiment_score,
        round(avg(positive_pct), 2) AS positive_sentiment_pct
    FROM vw_sentiment_daily
    WHERE full_date >= CURRENT_DATE - INTERVAL '30 days'
)
SELECT
    count(*) AS total_posts,
    sum(reach) AS total_reach,
    sum(impressions) AS total_impressions,
    sum(engagement_count) AS total_engagement,
    round(avg(engagement_rate), 4) AS avg_engagement_rate,
    round(avg(virality_score), 4) AS avg_virality_score,
    s.avg_sentiment_score,
    s.positive_sentiment_pct
FROM current_period cp
CROSS JOIN sentiment s
GROUP BY s.avg_sentiment_score, s.positive_sentiment_pct;

SELECT
    calendar_year,
    month_of_year,
    platform_name,
    sum(reach) AS total_reach,
    sum(engagement_count) AS total_engagement,
    round(avg(engagement_rate), 4) AS avg_engagement_rate
FROM vw_post_performance
GROUP BY calendar_year, month_of_year, platform_name
ORDER BY calendar_year, month_of_year, platform_name;
