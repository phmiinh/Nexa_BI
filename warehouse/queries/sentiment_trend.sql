SET search_path TO social_dw;

SELECT
    calendar_year,
    week_of_year,
    platform_name,
    sum(comment_count) AS comments_analyzed,
    sum(positive_count) AS positive_comments,
    sum(neutral_count) AS neutral_comments,
    sum(negative_count) AS negative_comments,
    round(avg(avg_sentiment_score), 4) AS avg_sentiment_score,
    round((sum(positive_count)::numeric / NULLIF(sum(comment_count), 0)) * 100, 2) AS positive_pct,
    round((sum(negative_count)::numeric / NULLIF(sum(comment_count), 0)) * 100, 2) AS negative_pct
FROM vw_sentiment_daily
GROUP BY calendar_year, week_of_year, platform_name
ORDER BY calendar_year, week_of_year, platform_name;

SELECT
    full_date,
    platform_name,
    page_name,
    negative_count,
    comment_count,
    negative_pct
FROM vw_sentiment_daily
WHERE comment_count >= 10
  AND negative_pct >= 30
ORDER BY full_date DESC, negative_pct DESC;
