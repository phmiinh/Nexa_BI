SET search_path TO social_dw;

SELECT
    content_type,
    content_category,
    count(*) AS post_count,
    sum(reach) AS total_reach,
    sum(impressions) AS total_impressions,
    sum(engagement_count) AS total_engagement,
    round(avg(engagement_rate), 4) AS avg_engagement_rate,
    round(avg(virality_score), 4) AS avg_virality_score
FROM vw_post_performance
WHERE is_competitor = false
GROUP BY content_type, content_category
ORDER BY avg_engagement_rate DESC, post_count DESC;

SELECT
    platform_name,
    width_bucket(reach, 0, NULLIF((SELECT max(reach) FROM vw_post_performance), 0), 10) AS reach_bucket,
    count(*) AS post_count,
    round(avg(engagement_rate), 4) AS avg_engagement_rate
FROM vw_post_performance
WHERE reach > 0
GROUP BY platform_name, reach_bucket
ORDER BY platform_name, reach_bucket;
