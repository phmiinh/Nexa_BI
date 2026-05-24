from __future__ import annotations

import os

os.environ["DATABASE_URL"] = ""
os.environ["SOCIALENS_DATABASE_URL"] = ""
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.sociallens_api.settings")

import django
import pytest
from django.test import Client


@pytest.fixture(scope="module", autouse=True)
def setup_django():
    django.setup()


@pytest.fixture()
def client() -> Client:
    return Client()


def test_health_endpoint(client: Client):
    response = client.get("/health/")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_posts_list_and_detail_use_processed_fallback(client: Client):
    response = client.get("/api/v1/posts/?limit=3")

    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "csv"
    assert payload["count"] == 3
    assert {"post_id", "platform", "engagement_rate"}.issubset(payload["results"][0])

    detail = client.get(f"/api/v1/posts/{payload['results'][0]['post_id']}/")

    assert detail.status_code == 200
    assert detail.json()["result"]["post_id"] == payload["results"][0]["post_id"]


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
def test_analytics_endpoints_return_json(client: Client, path: str):
    response = client.get(path)

    assert response.status_code == 200
    assert response["Content-Type"].startswith("application/json")
    assert response.json()


def test_insights_endpoint_returns_deterministic_vietnamese_messages(client: Client):
    response = client.get("/api/v1/analytics/insights/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "csv"
    assert len(payload["insights"]) >= 3
    assert {"type", "title", "message"}.issubset(payload["insights"][0])
    assert any("tương tác" in insight["message"] for insight in payload["insights"])


def test_sync_status_includes_current_counts_platforms_and_confidence(client: Client):
    response = client.get("/api/v1/sync/status/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["source_type"] == "csv"
    assert payload["counts"]["posts"] > 0
    assert payload["counts"]["comments"] > 0
    assert payload["platforms"] == ["youtube"]
    assert payload["source_confidence"]["level"] == "medium"
