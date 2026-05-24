CREATE SCHEMA IF NOT EXISTS social_dw;

SET search_path TO social_dw;

CREATE TABLE IF NOT EXISTS dim_time (
    time_id bigint PRIMARY KEY,
    full_date date NOT NULL,
    full_timestamp timestamptz NOT NULL,
    hour_of_day smallint NOT NULL CHECK (hour_of_day BETWEEN 0 AND 23),
    day_of_week smallint NOT NULL CHECK (day_of_week BETWEEN 1 AND 7),
    day_name varchar(9) NOT NULL,
    week_of_year smallint NOT NULL CHECK (week_of_year BETWEEN 1 AND 53),
    month_of_year smallint NOT NULL CHECK (month_of_year BETWEEN 1 AND 12),
    month_name varchar(9) NOT NULL,
    quarter_of_year smallint NOT NULL CHECK (quarter_of_year BETWEEN 1 AND 4),
    calendar_year smallint NOT NULL,
    is_weekend boolean NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT dim_time_unique_timestamp UNIQUE (full_timestamp)
);

CREATE TABLE IF NOT EXISTS dim_platform (
    platform_id smallserial PRIMARY KEY,
    platform_name varchar(40) NOT NULL UNIQUE,
    platform_type varchar(40) NOT NULL,
    api_source varchar(80),
    is_active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS dim_content_type (
    content_type_id smallserial PRIMARY KEY,
    type_name varchar(40) NOT NULL UNIQUE,
    type_category varchar(40) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS dim_page (
    page_id bigserial PRIMARY KEY,
    platform_id smallint NOT NULL REFERENCES dim_platform(platform_id),
    external_page_id varchar(255),
    page_name varchar(255) NOT NULL,
    industry varchar(120),
    country_code char(2),
    is_competitor boolean NOT NULL DEFAULT false,
    follower_count bigint NOT NULL DEFAULT 0 CHECK (follower_count >= 0),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT dim_page_unique_platform_external UNIQUE (platform_id, external_page_id),
    CONSTRAINT dim_page_unique_platform_name UNIQUE (platform_id, page_name)
);

CREATE TABLE IF NOT EXISTS fact_post (
    post_id bigserial PRIMARY KEY,
    external_post_id varchar(255) NOT NULL,
    platform_id smallint NOT NULL REFERENCES dim_platform(platform_id),
    time_id bigint NOT NULL REFERENCES dim_time(time_id),
    content_type_id smallint NOT NULL REFERENCES dim_content_type(content_type_id),
    page_id bigint NOT NULL REFERENCES dim_page(page_id),
    post_url text,
    caption text,
    hashtag_count integer NOT NULL DEFAULT 0 CHECK (hashtag_count >= 0),
    reach bigint NOT NULL DEFAULT 0 CHECK (reach >= 0),
    impressions bigint NOT NULL DEFAULT 0 CHECK (impressions >= 0),
    likes bigint NOT NULL DEFAULT 0 CHECK (likes >= 0),
    comments bigint NOT NULL DEFAULT 0 CHECK (comments >= 0),
    shares bigint NOT NULL DEFAULT 0 CHECK (shares >= 0),
    saves bigint NOT NULL DEFAULT 0 CHECK (saves >= 0),
    engagement_count bigint GENERATED ALWAYS AS (likes + comments + shares + saves) STORED,
    engagement_rate numeric(9,4) GENERATED ALWAYS AS (
        CASE WHEN reach > 0 THEN round(((likes + comments + shares + saves)::numeric / reach::numeric) * 100, 4) ELSE NULL END
    ) STORED,
    virality_score numeric(9,4) GENERATED ALWAYS AS (
        CASE WHEN reach > 0 THEN round((shares::numeric / reach::numeric) * 100, 4) ELSE NULL END
    ) STORED,
    loaded_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT fact_post_unique_source UNIQUE (platform_id, external_post_id)
);

CREATE TABLE IF NOT EXISTS fact_sentiment (
    sentiment_id bigserial PRIMARY KEY,
    external_comment_id varchar(255) NOT NULL,
    post_id bigint NOT NULL REFERENCES fact_post(post_id) ON DELETE CASCADE,
    platform_id smallint NOT NULL REFERENCES dim_platform(platform_id),
    time_id bigint NOT NULL REFERENCES dim_time(time_id),
    sentiment_label varchar(20) NOT NULL CHECK (sentiment_label IN ('positive', 'neutral', 'negative')),
    sentiment_score numeric(6,4) NOT NULL CHECK (sentiment_score BETWEEN -1 AND 1),
    comment_text text,
    loaded_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT fact_sentiment_unique_source UNIQUE (platform_id, external_comment_id)
);

CREATE TABLE IF NOT EXISTS etl_runs (
    run_id bigserial PRIMARY KEY,
    source varchar(100) NOT NULL,
    started_at timestamptz NOT NULL DEFAULT now(),
    finished_at timestamptz NOT NULL DEFAULT now(),
    status varchar(30) NOT NULL,
    extracted_posts integer NOT NULL DEFAULT 0 CHECK (extracted_posts >= 0),
    extracted_comments integer NOT NULL DEFAULT 0 CHECK (extracted_comments >= 0),
    loaded_posts integer NOT NULL DEFAULT 0 CHECK (loaded_posts >= 0),
    loaded_comments integer NOT NULL DEFAULT 0 CHECK (loaded_comments >= 0),
    error_message text
);

INSERT INTO dim_platform (platform_name, platform_type, api_source)
VALUES
    ('facebook', 'social_network', 'Facebook Graph API'),
    ('instagram', 'social_network', 'Meta Graph API'),
    ('tiktok', 'short_video', 'TikTok Research API'),
    ('youtube', 'video_platform', 'YouTube Data API v3')
ON CONFLICT (platform_name) DO NOTHING;

INSERT INTO dim_content_type (type_name, type_category)
VALUES
    ('text', 'post'),
    ('image', 'post'),
    ('video', 'video'),
    ('story', 'ephemeral'),
    ('reel', 'short_video'),
    ('short', 'short_video'),
    ('carousel', 'post'),
    ('livestream', 'video')
ON CONFLICT (type_name) DO NOTHING;
