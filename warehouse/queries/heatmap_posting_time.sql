SET search_path TO social_dw;

SELECT
    day_of_week,
    day_name,
    hour_of_day,
    platform_name,
    post_count,
    avg_engagement_rate,
    total_engagement
FROM vw_best_posting_heatmap
ORDER BY day_of_week, hour_of_day, platform_name;

SELECT
    platform_name,
    day_name,
    hour_of_day,
    avg_engagement_rate,
    post_count,
    dense_rank() OVER (
        PARTITION BY platform_name
        ORDER BY avg_engagement_rate DESC, total_engagement DESC
    ) AS time_slot_rank
FROM vw_best_posting_heatmap
WHERE post_count >= 3
ORDER BY platform_name, time_slot_rank
LIMIT 20;
