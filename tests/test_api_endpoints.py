from __future__ import annotations

import os

import pandas as pd

os.environ["DATABASE_URL"] = ""
os.environ["SOCIALENS_DATABASE_URL"] = ""
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.sociallens_api.settings")

import django
import pytest
from django.test import Client

from backend.sociallens_api.data import Repository, WarehouseUnavailable


@pytest.fixture(scope="module", autouse=True)
def setup_django():
    django.setup()


@pytest.fixture()
def client() -> Client:
    return Client()


@pytest.fixture(autouse=True)
def warehouse_query(monkeypatch: pytest.MonkeyPatch):
    def fake_query(_: Repository, sql: str, params: dict | None = None) -> pd.DataFrame:
        if "vw_post_performance" in sql:
            return pd.DataFrame(
                [
                    {
                        "post_id": 1,
                        "external_post_id": "yt_1",
                        "platform_name": "youtube",
                        "page_name": "Highlands Coffee Vietnam",
                        "content_type": "video",
                        "full_date": "2026-05-19",
                        "full_timestamp": "2026-05-19T10:00:00+07:00",
                        "hour_of_day": 10,
                        "reach": 1000,
                        "impressions": 1000,
                        "likes": 20,
                        "comments": 5,
                        "shares": 0,
                        "engagement_count": 25,
                        "engagement_rate": 2.5,
                        "virality_score": 0.0,
                        "sentiment_ratio": 50.0,
                        "caption": "Test video",
                    }
                ]
            )
        if "vw_executive_overview" in sql:
            return pd.DataFrame(
                [
                    {
                        "total_posts": 1,
                        "total_reach": 1000,
                        "total_impressions": 1000,
                        "total_engagement": 25,
                        "avg_engagement_rate": 2.5,
                        "avg_virality_score": 0.0,
                        "date_from": "2026-05-19",
                        "date_to": "2026-05-19",
                    }
                ]
            )
        if "vw_daily_engagement" in sql:
            return pd.DataFrame(
                [
                    {
                        "full_date": "2026-05-19",
                        "platform_name": "youtube",
                        "post_count": 1,
                        "total_reach": 1000,
                        "total_impressions": 1000,
                        "total_engagement": 25,
                        "avg_engagement_rate": 2.5,
                        "avg_virality_score": 0.0,
                        "comment_count": 2,
                        "positive_count": 1,
                        "share_of_voice": 100.0,
                        "sentiment_ratio": 50.0,
                    }
                ]
            )
        if "vw_sentiment_trend" in sql:
            return pd.DataFrame(
                [
                    {
                        "full_date": "2026-05-19",
                        "platform_name": "youtube",
                        "page_name": "Highlands Coffee Vietnam",
                        "comment_count": 2,
                        "positive_count": 1,
                        "neutral_count": 1,
                        "negative_count": 0,
                        "positive_pct": 50.0,
                        "negative_pct": 0.0,
                    }
                ]
            )
        if "vw_content_performance" in sql:
            return pd.DataFrame(
                [
                    {
                        "platform_name": "youtube",
                        "content_type": "video",
                        "is_competitor": False,
                        "post_count": 1,
                        "total_reach": 1000,
                        "total_impressions": 1000,
                        "total_engagement": 25,
                        "avg_engagement_rate": 2.5,
                        "avg_virality_score": 0.0,
                        "comment_count": 2,
                        "positive_count": 1,
                        "share_of_voice": 100.0,
                        "sentiment_ratio": 50.0,
                    }
                ]
            )
        if "vw_posting_time_heatmap" in sql:
            return pd.DataFrame(
                [
                    {
                        "day_of_week": 2,
                        "day_name": "Tuesday",
                        "hour_of_day": 10,
                        "platform_name": "youtube",
                        "post_count": 1,
                        "avg_engagement_rate": 2.5,
                        "total_engagement": 25,
                    }
                ]
            )
        if "vw_competitor_benchmark" in sql:
            return pd.DataFrame(
                [
                    {
                        "platform_name": "youtube",
                        "page_name": "Highlands Coffee Vietnam",
                        "industry": "F&B",
                        "is_competitor": False,
                        "post_count": 1,
                        "total_reach": 1000,
                        "total_engagement": 25,
                        "avg_engagement_rate": 2.5,
                        "avg_virality_score": 0.0,
                        "comment_count": 2,
                        "positive_count": 1,
                        "share_of_voice": 100.0,
                        "sentiment_ratio": 50.0,
                    }
                ]
            )
        if "vw_viral_posts" in sql:
            return pd.DataFrame(
                [
                    {
                        "post_id": 1,
                        "external_post_id": "yt_1",
                        "platform_name": "youtube",
                        "page_name": "Highlands Coffee Vietnam",
                        "content_type": "video",
                        "full_date": "2026-05-19",
                        "reach": 1000,
                        "engagement_count": 25,
                        "engagement_rate": 2.5,
                        "virality_score": 0.0,
                        "sentiment_ratio": 50.0,
                        "caption": "Test video",
                    }
                ]
            )
        if "FROM social_dw.etl_runs" in sql:
            return pd.DataFrame(
                [
                    {
                        "run_id": 1,
                        "source": "etl.cli",
                        "started_at": "2026-05-19T00:00:00+00:00",
                        "finished_at": "2026-05-19T00:01:00+00:00",
                        "status": "success",
                        "extracted_posts": 1,
                        "extracted_comments": 2,
                        "loaded_posts": 1,
                        "loaded_comments": 2,
                        "error_message": None,
                    }
                ]
            )
        if "fact_post" in sql and "fact_sentiment" in sql:
            return pd.DataFrame(
                [
                    {
                        "post_count": 1,
                        "comment_count": 2,
                        "data_from": "2026-05-19",
                        "data_through": "2026-05-19",
                        "platforms": "youtube",
                    }
                ]
            )
        if "fact_sentiment" in sql:
            return pd.DataFrame([{"sentiment_id": 1}])
        raise AssertionError(f"unexpected warehouse SQL: {sql}")

    monkeypatch.setattr(Repository, "_query", fake_query)


def test_health_endpoint(client: Client):
    response = client.get("/health/")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_posts_list_and_detail_use_warehouse(client: Client):
    response = client.get("/api/v1/posts/?limit=3")

    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {"count", "source", "results"}
    assert payload["source"] == "warehouse"
    assert payload["count"] == 1
    assert {"post_id", "platform", "engagement_rate", "sentiment_ratio"}.issubset(
        payload["results"][0]
    )

    detail = client.get(f"/api/v1/posts/{payload['results'][0]['post_id']}/")

    assert detail.status_code == 200
    assert detail.json()["source"] == "warehouse"
    assert detail.json()["result"]["post_id"] == payload["results"][0]["post_id"]


def test_post_detail_returns_404_for_unknown_post(client: Client):
    response = client.get("/api/v1/posts/does-not-exist/")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not found"}


def test_posts_list_uses_lightweight_spec_shape_not_drf_pagination(client: Client):
    response = client.get("/api/v1/posts/")

    assert response.status_code == 200
    payload = response.json()
    assert {"count", "source", "results"}.issubset(payload)
    assert "total_pages" not in payload
    assert "next" not in payload
    assert "previous" not in payload


def test_analytics_collection_endpoints_use_source_results_shape(client: Client):
    collection_paths = [
        "/api/v1/analytics/engagement/",
        "/api/v1/analytics/sentiment/",
        "/api/v1/analytics/top-posts/",
        "/api/v1/analytics/content-performance/",
        "/api/v1/analytics/heatmap/",
        "/api/v1/analytics/competitors/",
    ]

    for path in collection_paths:
        response = client.get(path)
        assert response.status_code == 200
        payload = response.json()
        assert set(payload) == {"source", "results"}
        assert payload["source"] == "warehouse"
        assert isinstance(payload["results"], list)


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/analytics/overview/",
        "/api/v1/analytics/engagement/",
        "/api/v1/analytics/sentiment/",
        "/api/v1/analytics/top-posts/",
        "/api/v1/analytics/content-performance/",
        "/api/v1/analytics/heatmap/",
        "/api/v1/analytics/competitors/",
        "/api/v1/analytics/insights/",
        "/api/v1/sync/status/",
    ],
)
def test_analytics_endpoints_return_json_from_warehouse(client: Client, path: str):
    response = client.get(path)

    assert response.status_code == 200
    assert response["Content-Type"].startswith("application/json")
    assert response.json()


def test_insights_endpoint_returns_deterministic_vietnamese_messages(client: Client):
    response = client.get("/api/v1/analytics/insights/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "warehouse"
    assert len(payload["insights"]) >= 3
    assert {"type", "title", "message"}.issubset(payload["insights"][0])
    assert any("2.5%" in insight["message"] for insight in payload["insights"])


def test_sync_status_includes_current_counts_platforms_and_confidence(client: Client):
    response = client.get("/api/v1/sync/status/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["source_type"] == "warehouse"
    assert payload["counts"]["posts"] == 1
    assert payload["counts"]["comments"] == 2
    assert payload["platforms"] == ["youtube"]
    assert payload["source_confidence"]["level"] == "high"


def test_api_returns_503_when_warehouse_is_unavailable(
    client: Client, monkeypatch: pytest.MonkeyPatch
):
    def raise_unavailable(_: Repository, __: str, ___: dict | None = None) -> pd.DataFrame:
        raise WarehouseUnavailable("database host secret detail")

    monkeypatch.setattr(Repository, "_query", raise_unavailable)

    response = client.get("/api/v1/analytics/overview/")

    assert response.status_code == 503
    payload = response.json()
    assert payload["source_type"] == "warehouse"
    assert payload["error_code"] == "WAREHOUSE_UNAVAILABLE"
    assert "database host secret detail" not in str(payload)


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/posts/",
        "/api/v1/posts/yt_1/",
        "/api/v1/analytics/overview/",
        "/api/v1/analytics/engagement/",
        "/api/v1/analytics/sentiment/",
        "/api/v1/analytics/top-posts/",
        "/api/v1/analytics/content-performance/",
        "/api/v1/analytics/heatmap/",
        "/api/v1/analytics/competitors/",
        "/api/v1/analytics/insights/",
        "/api/v1/sync/status/",
    ],
)
def test_warehouse_backed_endpoints_return_sanitized_503(
    client: Client, monkeypatch: pytest.MonkeyPatch, path: str
):
    def raise_unavailable(_: Repository, __: str, ___: dict | None = None) -> pd.DataFrame:
        raise WarehouseUnavailable("warehouse password=secret host=172.16.4.81")

    monkeypatch.setattr(Repository, "_query", raise_unavailable)

    response = client.get(path)

    assert response.status_code == 503
    payload = response.json()
    assert payload == {
        "detail": "Warehouse unavailable",
        "source_type": "warehouse",
        "error_code": "WAREHOUSE_UNAVAILABLE",
    }
    assert "secret" not in str(payload)
    assert "172.16.4.81" not in str(payload)


def test_competitors_include_share_of_voice_and_sentiment_ratio(client: Client):
    response = client.get("/api/v1/analytics/competitors/")

    assert response.status_code == 200
    row = response.json()["results"][0]
    assert row["share_of_voice"] == 100.0
    assert row["sentiment_ratio"] == 50.0


def test_top_posts_limit_clamps_to_positive_value(client: Client):
    response = client.get("/api/v1/analytics/top-posts/?limit=0")

    assert response.status_code == 200
    assert len(response.json()["results"]) == 1


def test_time_series_limits_are_clamped_before_querying_warehouse(
    client: Client, monkeypatch: pytest.MonkeyPatch
):
    seen: list[dict | None] = []

    def fake_query(_: Repository, sql: str, params: dict | None = None) -> pd.DataFrame:
        seen.append(params)
        if "vw_daily_engagement" in sql:
            return pd.DataFrame(
                [
                    {
                        "full_date": "2026-05-19",
                        "platform_name": "youtube",
                        "post_count": 1,
                        "total_reach": 1000,
                        "total_impressions": 1000,
                        "total_engagement": 25,
                        "avg_engagement_rate": 2.5,
                        "avg_virality_score": 0.0,
                    }
                ]
            )
        if "vw_sentiment_trend" in sql:
            return pd.DataFrame(
                [
                    {
                        "full_date": "2026-05-19",
                        "platform_name": "youtube",
                        "page_name": "Highlands Coffee Vietnam",
                        "comment_count": 2,
                        "positive_count": 1,
                        "neutral_count": 1,
                        "negative_count": 0,
                        "positive_pct": 50.0,
                        "negative_pct": 0.0,
                    }
                ]
            )
        raise AssertionError(f"unexpected warehouse SQL: {sql}")

    monkeypatch.setattr(Repository, "_query", fake_query)

    assert client.get("/api/v1/analytics/engagement/?limit=9999").status_code == 200
    assert client.get("/api/v1/analytics/sentiment/?limit=bad").status_code == 200

    assert seen == [{"limit": 500}, {"limit": 120}]
