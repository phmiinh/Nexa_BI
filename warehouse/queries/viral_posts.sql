SET search_path TO social_dw;

SELECT
    post_id,
    external_post_id,
    full_timestamp,
    platform_name,
    page_name,
    is_competitor,
    content_type,
    reach,
    shares,
    engagement_count,
    engagement_rate,
    virality_score,
    post_url,
    left(caption, 240) AS caption_preview
FROM vw_post_performance
WHERE reach >= 100
ORDER BY virality_score DESC, engagement_rate DESC, shares DESC
LIMIT 25;

SELECT
    platform_name,
    content_type,
    percentile_cont(0.9) WITHIN GROUP (ORDER BY virality_score) AS p90_virality_score,
    percentile_cont(0.9) WITHIN GROUP (ORDER BY engagement_rate) AS p90_engagement_rate
FROM vw_post_performance
GROUP BY platform_name, content_type
ORDER BY platform_name, content_type;
