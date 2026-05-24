SET search_path TO social_dw;

SELECT
    platform_name,
    content_type,
    count(*) AS post_count,
    sum(reach) AS total_reach,
    sum(engagement_count) AS total_engagement,
    round(avg(engagement_rate), 4) AS avg_engagement_rate,
    round(percentile_cont(0.5) WITHIN GROUP (ORDER BY engagement_rate)::numeric, 4) AS median_engagement_rate
FROM vw_post_performance
WHERE is_competitor = false
GROUP BY platform_name, content_type
ORDER BY avg_engagement_rate DESC NULLS LAST, total_engagement DESC;

SELECT
    full_date,
    platform_name,
    sum(reach) AS reach,
    sum(engagement_count) AS engagement,
    round(avg(engagement_rate), 4) AS avg_engagement_rate
FROM vw_post_performance
GROUP BY full_date, platform_name
ORDER BY full_date, platform_name;
