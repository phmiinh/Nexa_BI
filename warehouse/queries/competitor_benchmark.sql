SET search_path TO social_dw;

SELECT
    platform_name,
    industry,
    CASE WHEN is_competitor THEN 'competitor' ELSE 'owned' END AS page_group,
    count(*) AS post_count,
    sum(reach) AS total_reach,
    sum(engagement_count) AS total_engagement,
    round(avg(engagement_rate), 4) AS avg_engagement_rate,
    round(avg(virality_score), 4) AS avg_virality_score
FROM vw_post_performance
GROUP BY platform_name, industry, is_competitor
ORDER BY platform_name, industry, page_group;

SELECT
    p.platform_name,
    pg.page_name,
    pg.is_competitor,
    pg.follower_count,
    count(fp.post_id) AS post_count,
    sum(fp.reach) AS total_reach,
    sum(fp.engagement_count) AS total_engagement,
    round(avg(fp.engagement_rate), 4) AS avg_engagement_rate
FROM fact_post fp
JOIN dim_page pg ON pg.page_id = fp.page_id
JOIN dim_platform p ON p.platform_id = fp.platform_id
GROUP BY p.platform_name, pg.page_name, pg.is_competitor, pg.follower_count
ORDER BY avg_engagement_rate DESC NULLS LAST, total_engagement DESC;
