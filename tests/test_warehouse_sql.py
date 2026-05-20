from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_sql(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8").lower()


def test_schema_defines_required_tables_and_schema():
    ddl = read_sql("warehouse/schema/001_schema.sql")

    assert "create schema if not exists social_dw" in ddl
    for table in [
        "dim_time",
        "dim_platform",
        "dim_content_type",
        "dim_page",
        "fact_post",
        "fact_sentiment",
    ]:
        assert f"create table if not exists {table}" in ddl


def test_schema_has_core_constraints_and_generated_metrics():
    ddl = read_sql("warehouse/schema/001_schema.sql")

    assert "references dim_platform" in ddl
    assert "references dim_time" in ddl
    assert "references dim_content_type" in ddl
    assert "references dim_page" in ddl
    assert "generated always as" in ddl
    assert "engagement_rate" in ddl
    assert "virality_score" in ddl
    assert "sentiment_label in ('positive', 'neutral', 'negative')" in ddl


def test_indexes_and_views_cover_dashboard_access_patterns():
    indexes = read_sql("warehouse/schema/002_indexes.sql")
    views = read_sql("warehouse/schema/003_views.sql")

    for index_name in [
        "idx_fact_post_platform_time",
        "idx_fact_post_page_time",
        "idx_fact_post_engagement_rate",
        "idx_fact_sentiment_label_time",
    ]:
        assert index_name in indexes

    for view_name in [
        "vw_post_performance",
        "vw_sentiment_daily",
        "vw_platform_content_summary",
        "vw_best_posting_heatmap",
        "vw_executive_overview",
        "vw_daily_engagement",
        "vw_sentiment_trend",
        "vw_content_performance",
        "vw_competitor_benchmark",
        "vw_posting_time_heatmap",
        "vw_viral_posts",
    ]:
        assert f"view {view_name}" in views


def test_required_analytical_queries_exist():
    expected_files = [
        "executive_overview.sql",
        "engagement_analysis.sql",
        "sentiment_trend.sql",
        "content_performance.sql",
        "competitor_benchmark.sql",
        "heatmap_posting_time.sql",
        "viral_posts.sql",
    ]

    for file_name in expected_files:
        path = ROOT / "warehouse" / "queries" / file_name
        assert path.exists(), file_name
        sql = path.read_text(encoding="utf-8").lower()
        assert "set search_path to social_dw" in sql
        assert "select" in sql
