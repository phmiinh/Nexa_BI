from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
import requests

from etl.extractors import ExtractError
from etl.extractors import extract_youtube, fetch_youtube_comments
from etl.extractors import raise_youtube_for_status
from etl.normalize import normalize_dataset
from etl.pipeline import run_pipeline
from etl.sample import load_sample_data
from etl.sentiment import analyze_sentiment


class FakeResponse:
    def __init__(self, payload: dict[str, Any], status_code: int = 200, reason: str = "OK") -> None:
        self.payload = payload
        self.status_code = status_code
        self.reason = reason

    def json(self) -> dict[str, Any]:
        return self.payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            error = requests.HTTPError(f"{self.status_code} {self.reason}")
            error.response = self
            raise error


class SecretUrlResponse(FakeResponse):
    url = "https://www.googleapis.com/youtube/v3/channels?key=secret-key"

    def raise_for_status(self) -> None:
        error = requests.HTTPError(f"{self.status_code} {self.reason} for url: {self.url}")
        error.response = self
        raise error


class FakeYouTubeSession:
    def __init__(self, video_ids: list[str] | None = None, fail_comments: bool = False) -> None:
        self.video_ids = video_ids or ["video_1", "video_2", "video_2", "video_3"]
        self.fail_comments = fail_comments
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def get(self, url: str, params: dict[str, Any], timeout: int) -> FakeResponse:
        self.calls.append((url, params))
        if "channels" in url:
            return FakeResponse(
                {
                    "items": [
                        {
                            "contentDetails": {
                                "relatedPlaylists": {"uploads": "uploads_playlist"}
                            }
                        }
                    ]
                }
            )
        if "playlistItems" in url:
            page_token = params.get("pageToken")
            if not page_token:
                return FakeResponse(
                    {
                        "items": [
                            {"contentDetails": {"videoId": self.video_ids[0]}},
                            {"contentDetails": {"videoId": self.video_ids[1]}},
                        ],
                        "nextPageToken": "next-page",
                    }
                )
            return FakeResponse(
                {
                    "items": [
                        {"contentDetails": {"videoId": video_id}}
                        for video_id in self.video_ids[2:]
                    ]
                }
            )
        if "videos" in url:
            ids = str(params["id"]).split(",")
            return FakeResponse(
                {
                    "items": [
                        {
                            "id": video_id,
                            "snippet": {
                                "channelId": "channel_1",
                                "channelTitle": "Highlands Coffee Vietnam",
                                "title": f"Video {video_id}",
                                "publishedAt": "2026-05-19T00:00:00Z",
                            },
                            "statistics": {
                                "viewCount": "1000",
                                "likeCount": "20",
                                "commentCount": "5",
                            },
                        }
                        for video_id in ids
                    ]
                }
            )
        if "commentThreads" in url:
            if self.fail_comments:
                return FakeResponse({}, status_code=403, reason="Forbidden")
            return FakeResponse(
                {
                    "items": [
                        {
                            "id": f"thread_{params['videoId']}",
                            "snippet": {
                                "topLevelComment": {
                                    "id": f"comment_{params['videoId']}",
                                    "snippet": {
                                        "authorChannelId": {"value": "author_1"},
                                        "authorDisplayName": "Author",
                                        "textDisplay": "Dich vu tot",
                                        "publishedAt": "2026-05-19T01:00:00Z",
                                    },
                                }
                            },
                        }
                    ]
                }
            )
        raise AssertionError(f"unexpected URL: {url}")


def test_normalize_posts_and_comments_contract():
    tables = normalize_dataset(load_sample_data())

    posts = tables["posts"]
    comments = tables["comments"]

    assert len(posts) >= 500
    assert len(comments) >= 1000
    assert {"post_id", "platform", "engagement_rate", "virality_score"}.issubset(posts.columns)
    assert {"comment_id", "sentiment_label", "sentiment_score"}.issubset(comments.columns)
    first = posts.iloc[0]
    expected = round(
        (first["likes"] + first["comments_count"] + first["shares"]) / first["reach"] * 100,
        4,
    )
    assert first["engagement_rate"] == expected


def test_normalize_deduplicates_by_platform_and_external_id():
    tables = normalize_dataset(
        {
            "posts": [
                {"id": "same", "platform": "youtube", "publishedAt": "2026-01-01T00:00:00Z"},
                {"id": "same", "platform": "facebook", "created_time": "2026-01-01T00:00:00Z"},
            ],
            "comments": [
                {"id": "same", "post_id": "same", "platform": "youtube", "created_time": "2026-01-01T00:00:00Z"},
                {"id": "same", "post_id": "same", "platform": "facebook", "created_time": "2026-01-01T00:00:00Z"},
            ],
        }
    )

    assert len(tables["posts"]) == 2
    assert len(tables["comments"]) == 2


def test_vietnamese_rule_sentiment():
    assert analyze_sentiment("Dich vu tot, minh rat thich").label == "positive"
    assert analyze_sentiment("App bi loi va giao hang cham").label == "negative"
    assert analyze_sentiment("Da nhan thong tin").label == "neutral"


def test_pipeline_writes_csv_outputs(tmp_path: Path):
    result = run_pipeline(source="sample", output_dir=str(tmp_path))

    assert result.quality.passed
    assert Path(result.outputs["csv"]["posts"]).exists()
    assert Path(result.outputs["csv"]["comments"]).exists()
    assert Path(result.outputs["raw"]["posts"]).exists()


def test_cli_json_source(tmp_path: Path):
    fixture = Path(__file__).parent / "fixtures" / "social_sample.json"
    output_dir = tmp_path / "processed"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "etl.cli",
            "--source",
            "json",
            "--input-path",
            str(fixture),
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)
    assert payload["normalized_posts"] == 1
    assert payload["normalized_comments"] == 2
    assert (output_dir / "posts.csv").exists()


def test_cli_run_subcommand_sample(tmp_path: Path):
    output_dir = tmp_path / "processed"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "etl.cli",
            "run",
            "--sources",
            "sample",
            "--output-dir",
            str(output_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(completed.stdout)
    assert len(payload["runs"]) == 1
    assert (output_dir / "posts.csv").exists()


def test_youtube_missing_config_raises_without_sample_data(monkeypatch):
    import etl.pipeline as pipeline

    def raise_missing_credentials(**_: Any) -> dict[str, list[dict[str, Any]]]:
        raise ExtractError("YOUTUBE_API_KEY is required for youtube source")

    monkeypatch.setattr(pipeline, "extract_youtube", raise_missing_credentials)

    with pytest.raises(ExtractError, match="YOUTUBE_API_KEY is required"):
        pipeline.extract_source("youtube", limit=1)


@pytest.mark.parametrize(
    "api_error",
    [
        ExtractError("YouTube quota exceeded"),
        requests.HTTPError("403 Client Error: Forbidden for url"),
    ],
)
def test_youtube_api_errors_raise_without_sample_data(monkeypatch, api_error):
    import etl.pipeline as pipeline

    def raise_api_error(**_: Any) -> dict[str, list[dict[str, Any]]]:
        raise api_error

    monkeypatch.setattr(pipeline, "extract_youtube", raise_api_error)

    with pytest.raises(type(api_error)):
        pipeline.extract_source(
            "youtube",
            query="Highlands Coffee",
            limit=2,
        )


def test_youtube_source_raises_when_api_config_missing(monkeypatch):
    import etl.pipeline as pipeline

    class UnexpectedSession:
        def __init__(self) -> None:
            raise AssertionError("missing config should fail before external API calls")

    monkeypatch.setenv("YOUTUBE_API_KEY", "")
    monkeypatch.setattr(requests, "Session", UnexpectedSession)

    with pytest.raises(ExtractError, match="YOUTUBE_API_KEY is required"):
        pipeline.extract_source(
            "youtube",
            query="Highlands Coffee",
            limit=1,
        )


def test_youtube_channel_uses_uploads_playlist_and_clamps_limits():
    session = FakeYouTubeSession()

    result = extract_youtube(
        channel_id="channel_1",
        api_key="secret-key",
        limit=99,
        comments_limit=150,
        max_search_pages=2,
        session=session,
    )

    urls = [url for url, _ in session.calls]
    assert any("channels" in url for url in urls)
    assert any("playlistItems" in url for url in urls)
    assert not any("search" in url for url in urls)
    assert [post["id"] for post in result["posts"]] == ["video_1", "video_2", "video_3"]
    playlist_calls = [params for url, params in session.calls if "playlistItems" in url]
    comment_calls = [params for url, params in session.calls if "commentThreads" in url]
    assert playlist_calls[0]["maxResults"] == 50
    assert {params["maxResults"] for params in comment_calls} == {100}


def test_youtube_comments_limit_zero_disables_comment_calls():
    session = FakeYouTubeSession()

    result = extract_youtube(
        channel_id="channel_1",
        api_key="secret-key",
        limit=50,
        comments_limit=0,
        max_search_pages=1,
        session=session,
    )

    assert result["posts"]
    assert result["comments"] == []
    assert not any("commentThreads" in url for url, _ in session.calls)


def test_youtube_video_details_are_chunked_at_50():
    session = FakeYouTubeSession(video_ids=[f"video_{index}" for index in range(55)])

    extract_youtube(
        channel_id="channel_1",
        api_key="secret-key",
        limit=50,
        comments_limit=0,
        max_search_pages=2,
        session=session,
    )

    video_calls = [params["id"].split(",") for url, params in session.calls if "videos" in url]
    assert [len(chunk) for chunk in video_calls] == [50, 5]


def test_youtube_comment_errors_are_sanitized(caplog):
    session = FakeYouTubeSession(fail_comments=True)

    comments = fetch_youtube_comments(session, "secret-key", "video_1", limit=100)

    assert comments == []
    assert "video_1" in caplog.text
    assert "secret-key" not in caplog.text
    assert "commentThreads" not in caplog.text


def test_youtube_status_errors_do_not_chain_secret_urls():
    response = SecretUrlResponse({}, status_code=403, reason="Forbidden")

    with pytest.raises(ExtractError) as exc_info:
        raise_youtube_for_status(response, "channels.list")

    assert str(exc_info.value) == "YouTube channels.list failed: 403 Forbidden"
    assert exc_info.value.__cause__ is None
    assert "secret-key" not in str(exc_info.value)
    assert "googleapis" not in str(exc_info.value)


def test_run_pipeline_youtube_raises_when_api_config_missing(
    monkeypatch, tmp_path: Path
):
    class UnexpectedSession:
        def __init__(self) -> None:
            raise AssertionError("missing config should fail before external API calls")

    monkeypatch.setenv("YOUTUBE_API_KEY", "")
    monkeypatch.setattr(requests, "Session", UnexpectedSession)

    with pytest.raises(ExtractError, match="YOUTUBE_API_KEY is required"):
        run_pipeline(
            source="youtube",
            output_dir=str(tmp_path),
            query="Highlands Coffee",
            limit=1,
        )


def test_cli_run_youtube_fails_when_api_config_missing(
    monkeypatch, tmp_path: Path, capsys
):
    import etl.cli as cli

    class UnexpectedSession:
        def __init__(self) -> None:
            raise AssertionError("missing config should fail before external API calls")

    monkeypatch.setenv("YOUTUBE_API_KEY", "")
    monkeypatch.delenv("YOUTUBE_CHANNEL_IDS", raising=False)
    monkeypatch.delenv("YOUTUBE_QUERIES", raising=False)
    monkeypatch.setattr(requests, "Session", UnexpectedSession)

    exit_code = cli.main(
        [
            "run",
            "--sources",
            "youtube",
            "--output-dir",
            str(tmp_path),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""


def test_cli_run_youtube_expands_queries_without_facebook(monkeypatch, tmp_path: Path, capsys):
    import etl.cli as cli

    calls: list[dict[str, Any]] = []

    class PipelineStub:
        def __init__(self, payload: dict[str, Any]) -> None:
            self.payload = payload

        def as_dict(self) -> dict[str, Any]:
            return self.payload

    def fake_run_pipeline(**kwargs: Any) -> PipelineStub:
        calls.append(kwargs)
        return PipelineStub(
            {
                "source": kwargs["source"],
                "query": kwargs["query"],
                "channel_id": kwargs["channel_id"],
                "page_id": kwargs["page_id"],
                "comments_limit": kwargs["comments_limit"],
                "max_search_pages": kwargs["max_search_pages"],
            }
        )

    monkeypatch.setenv("YOUTUBE_QUERIES", "Highlands Coffee, Phuc Long")
    monkeypatch.delenv("YOUTUBE_CHANNEL_IDS", raising=False)
    monkeypatch.delenv("FACEBOOK_ACCESS_TOKEN", raising=False)
    monkeypatch.setattr(cli, "run_pipeline", fake_run_pipeline)

    exit_code = cli.main(
        [
            "run",
            "--sources",
            "youtube",
            "--output-dir",
            str(tmp_path),
            "--limit",
            "7",
            "--comments-limit",
            "11",
            "--max-search-pages",
            "3",
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert [call["source"] for call in calls] == ["youtube", "youtube"]
    assert [call["query"] for call in calls] == ["Highlands Coffee", "Phuc Long"]
    assert [call["page_id"] for call in calls] == [None, None]
    assert [call["limit"] for call in calls] == [7, 7]
    assert [call["comments_limit"] for call in calls] == [11, 11]
    assert [call["max_search_pages"] for call in calls] == [3, 3]
    assert payload["runs"] == [
        {
            "source": "youtube",
            "query": "Highlands Coffee",
            "channel_id": None,
            "page_id": None,
            "comments_limit": 11,
            "max_search_pages": 3,
        },
        {
            "source": "youtube",
            "query": "Phuc Long",
            "channel_id": None,
            "page_id": None,
            "comments_limit": 11,
            "max_search_pages": 3,
        },
    ]


def test_cli_multi_source_loads_consolidated_warehouse_once(monkeypatch, tmp_path: Path, capsys):
    import etl.cli as cli

    calls: list[dict[str, Any]] = []
    load_calls: list[dict[str, Any]] = []

    class PipelineStub:
        def __init__(self, payload: dict[str, Any]) -> None:
            self.payload = payload

        def as_dict(self) -> dict[str, Any]:
            return self.payload

    def fake_run_pipeline(**kwargs: Any) -> PipelineStub:
        calls.append(kwargs)
        source_id = kwargs["channel_id"]
        raw_dir = tmp_path / "raw" / source_id
        raw_dir.mkdir(parents=True)
        posts_path = raw_dir / "posts.jsonl"
        comments_path = raw_dir / "comments.jsonl"
        posts_path.write_text(
            json.dumps(
                {
                    "id": f"post_{source_id}",
                    "platform": "youtube",
                    "channel_id": source_id,
                    "channel_title": source_id,
                    "title": "Video",
                    "publishedAt": "2026-05-19T00:00:00Z",
                    "views": 100,
                    "likes": 10,
                    "comment_count": 1,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        comments_path.write_text(
            json.dumps(
                {
                    "id": f"comment_{source_id}",
                    "post_id": f"post_{source_id}",
                    "platform": "youtube",
                    "text": "tot",
                    "created_time": "2026-05-19T01:00:00Z",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        return PipelineStub(
            {
                "source": "youtube",
                "outputs": {"raw": {"posts": str(posts_path), "comments": str(comments_path)}},
            }
        )

    def fake_load_sql(tables: dict[str, Any], database_url: str, run_source: str, **_: Any) -> dict[str, int]:
        load_calls.append(
            {
                "posts": len(tables["posts"]),
                "comments": len(tables["comments"]),
                "database_url": database_url,
                "run_source": run_source,
            }
        )
        return {"social_dw.fact_post": len(tables["posts"]), "social_dw.fact_sentiment": len(tables["comments"])}

    monkeypatch.setenv("YOUTUBE_CHANNEL_IDS", "channel_a,channel_b")
    monkeypatch.delenv("YOUTUBE_QUERIES", raising=False)
    monkeypatch.setattr(cli, "run_pipeline", fake_run_pipeline)
    monkeypatch.setattr(cli, "load_sql", fake_load_sql)

    exit_code = cli.main(
        [
            "run",
            "--sources",
            "youtube",
            "--output-dir",
            str(tmp_path / "processed"),
            "--database-url",
            "postgresql://warehouse",
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert [call["database_url"] for call in calls] == [None, None]
    assert load_calls == [
        {
            "posts": 2,
            "comments": 2,
            "database_url": "postgresql://warehouse",
            "run_source": "etl.cli:youtube:consolidated",
        }
    ]
    assert payload["consolidated"]["sql"]["social_dw.fact_post"] == 2
