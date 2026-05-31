SET search_path TO social_dw;

CREATE OR REPLACE VIEW vw_post_performance AS
WITH sentiment_by_post AS (
    SELECT
        post_id,
        count(*) AS loaded_comment_count,
        count(*) FILTER (WHERE sentiment_label = 'positive') AS positive_comment_count,
        count(*) FILTER (WHERE sentiment_label = 'neutral') AS neutral_comment_count,
        count(*) FILTER (WHERE sentiment_label = 'negative') AS negative_comment_count
    FROM fact_sentiment
    GROUP BY post_id
)
SELECT
    fp.post_id,
    fp.external_post_id,
    dt.full_date,
    dt.full_timestamp,
    dt.hour_of_day,
    dt.day_name,
    dt.day_of_week,
    dt.week_of_year,
    dt.month_of_year,
    dt.calendar_year,
    dp.platform_name,
    dpg.page_name,
    dpg.industry,
    dpg.is_competitor,
    dct.type_name AS content_type,
    dct.type_category AS content_category,
    fp.reach,
    fp.impressions,
    fp.likes,
    fp.comments,
    fp.shares,
    fp.saves,
    fp.engagement_count,
    fp.engagement_rate,
    fp.virality_score,
    fp.post_url,
    fp.caption,
    coalesce(sbp.loaded_comment_count, 0) AS loaded_comment_count,
    coalesce(sbp.positive_comment_count, 0) AS positive_comment_count,
    coalesce(sbp.neutral_comment_count, 0) AS neutral_comment_count,
    coalesce(sbp.negative_comment_count, 0) AS negative_comment_count,
    round((coalesce(sbp.positive_comment_count, 0)::numeric / NULLIF(coalesce(sbp.loaded_comment_count, 0), 0)) * 100, 2) AS sentiment_ratio
FROM fact_post fp
JOIN dim_time dt ON dt.time_id = fp.time_id
JOIN dim_platform dp ON dp.platform_id = fp.platform_id
JOIN dim_content_type dct ON dct.content_type_id = fp.content_type_id
JOIN dim_page dpg ON dpg.page_id = fp.page_id
LEFT JOIN sentiment_by_post sbp ON sbp.post_id = fp.post_id;

CREATE OR REPLACE VIEW vw_sentiment_daily AS
SELECT
    dt.full_date,
    dt.week_of_year,
    dt.month_of_year,
    dt.calendar_year,
    dp.platform_name,
    dpg.page_name,
    dpg.is_competitor,
    count(*) AS comment_count,
    count(*) FILTER (WHERE fs.sentiment_label = 'positive') AS positive_count,
    count(*) FILTER (WHERE fs.sentiment_label = 'neutral') AS neutral_count,
    count(*) FILTER (WHERE fs.sentiment_label = 'negative') AS negative_count,
    round(avg(fs.sentiment_score), 4) AS avg_sentiment_score,
    round((count(*) FILTER (WHERE fs.sentiment_label = 'positive')::numeric / NULLIF(count(*), 0)) * 100, 2) AS positive_pct,
    round((count(*) FILTER (WHERE fs.sentiment_label = 'negative')::numeric / NULLIF(count(*), 0)) * 100, 2) AS negative_pct
FROM fact_sentiment fs
JOIN fact_post fp ON fp.post_id = fs.post_id
JOIN dim_time dt ON dt.time_id = fs.time_id
JOIN dim_platform dp ON dp.platform_id = fs.platform_id
JOIN dim_page dpg ON dpg.page_id = fp.page_id
GROUP BY
    dt.full_date,
    dt.week_of_year,
    dt.month_of_year,
    dt.calendar_year,
    dp.platform_name,
    dpg.page_name,
    dpg.is_competitor;

CREATE OR REPLACE VIEW vw_platform_content_summary AS
SELECT
    platform_name,
    content_type,
    is_competitor,
    count(*) AS post_count,
    sum(reach) AS total_reach,
    sum(impressions) AS total_impressions,
    sum(engagement_count) AS total_engagement,
    round(avg(engagement_rate), 4) AS avg_engagement_rate,
    round(avg(virality_score), 4) AS avg_virality_score
FROM vw_post_performance
GROUP BY platform_name, content_type, is_competitor;

CREATE OR REPLACE VIEW vw_best_posting_heatmap AS
SELECT
    day_of_week,
    day_name,
    hour_of_day,
    platform_name,
    count(*) AS post_count,
    round(avg(engagement_rate), 4) AS avg_engagement_rate,
    sum(engagement_count) AS total_engagement
FROM vw_post_performance
GROUP BY day_of_week, day_name, hour_of_day, platform_name;

CREATE OR REPLACE VIEW vw_executive_overview AS
SELECT
    count(*) AS total_posts,
    sum(reach) AS total_reach,
    sum(impressions) AS total_impressions,
    sum(engagement_count) AS total_engagement,
    round(avg(engagement_rate), 4) AS avg_engagement_rate,
    round(avg(virality_score), 4) AS avg_virality_score,
    min(full_date) AS date_from,
    max(full_date) AS date_to
FROM vw_post_performance;

CREATE OR REPLACE VIEW vw_daily_engagement AS
SELECT
    full_date,
    platform_name,
    count(*) AS post_count,
    sum(reach) AS total_reach,
    sum(impressions) AS total_impressions,
    sum(engagement_count) AS total_engagement,
    round(avg(engagement_rate), 4) AS avg_engagement_rate,
    round(avg(virality_score), 4) AS avg_virality_score
FROM vw_post_performance
GROUP BY full_date, platform_name;

CREATE OR REPLACE VIEW vw_sentiment_trend AS
SELECT *
FROM vw_sentiment_daily;

CREATE OR REPLACE VIEW vw_content_performance AS
SELECT *
FROM vw_platform_content_summary;

CREATE OR REPLACE VIEW vw_competitor_benchmark AS
WITH page_performance AS (
    SELECT
        platform_name,
        page_name,
        industry,
        is_competitor,
        count(*) AS post_count,
        sum(reach) AS total_reach,
        sum(engagement_count) AS total_engagement,
        round(avg(engagement_rate), 4) AS avg_engagement_rate,
        round(avg(virality_score), 4) AS avg_virality_score,
        sum(loaded_comment_count) AS comment_count,
        sum(positive_comment_count) AS positive_count
    FROM vw_post_performance
    GROUP BY platform_name, page_name, industry, is_competitor
)
SELECT
    platform_name,
    page_name,
    industry,
    is_competitor,
    post_count,
    total_reach,
    total_engagement,
    avg_engagement_rate,
    avg_virality_score,
    comment_count,
    positive_count,
    round((total_reach::numeric / NULLIF(sum(total_reach) OVER (PARTITION BY platform_name), 0)) * 100, 2) AS share_of_voice,
    round((positive_count::numeric / NULLIF(comment_count, 0)) * 100, 2) AS sentiment_ratio
FROM page_performance;

CREATE OR REPLACE VIEW vw_posting_time_heatmap AS
SELECT *
FROM vw_best_posting_heatmap;

CREATE OR REPLACE VIEW vw_viral_posts AS
SELECT
    post_id,
    external_post_id,
    platform_name,
    page_name,
    content_type,
    full_date,
    reach,
    engagement_count,
    engagement_rate,
    virality_score,
    caption,
    loaded_comment_count,
    positive_comment_count,
    sentiment_ratio
FROM vw_post_performance
ORDER BY virality_score DESC NULLS LAST, engagement_count DESC NULLS LAST;
