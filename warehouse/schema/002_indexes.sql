SET search_path TO social_dw;

CREATE INDEX IF NOT EXISTS idx_dim_time_date ON dim_time (full_date);
CREATE INDEX IF NOT EXISTS idx_dim_time_calendar ON dim_time (calendar_year, month_of_year, week_of_year);
CREATE INDEX IF NOT EXISTS idx_dim_page_competitor ON dim_page (is_competitor, industry);
CREATE INDEX IF NOT EXISTS idx_fact_post_time ON fact_post (time_id);
CREATE INDEX IF NOT EXISTS idx_fact_post_platform_time ON fact_post (platform_id, time_id);
CREATE INDEX IF NOT EXISTS idx_fact_post_page_time ON fact_post (page_id, time_id);
CREATE INDEX IF NOT EXISTS idx_fact_post_content_time ON fact_post (content_type_id, time_id);
CREATE INDEX IF NOT EXISTS idx_fact_post_engagement_rate ON fact_post (engagement_rate DESC);
CREATE INDEX IF NOT EXISTS idx_fact_post_viral ON fact_post (virality_score DESC, shares DESC);
CREATE INDEX IF NOT EXISTS idx_fact_sentiment_post ON fact_sentiment (post_id);
CREATE INDEX IF NOT EXISTS idx_fact_sentiment_platform_time ON fact_sentiment (platform_id, time_id);
CREATE INDEX IF NOT EXISTS idx_fact_sentiment_label_time ON fact_sentiment (sentiment_label, time_id);
