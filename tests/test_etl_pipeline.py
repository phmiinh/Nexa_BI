from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
import requests

from etl.extractors import ExtractError
from etl.normalize import normalize_dataset
from etl.pipeline import run_pipeline
from etl.sample import load_sample_data
from etl.sentiment import analyze_sentiment


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


def test_vietnamese_rule_sentiment():
    assert analyze_sentiment("Dich vu tot, minh rat thich").label == "positive"
    assert analyze_sentiment("App bi loi va giao hang cham").label == "negative"
    assert analyze_sentiment("Da nhan thong tin").label == "neutral"


def test_pipeline_writes_csv_outputs(tmp_path: Path):
    result = run_pipeline(output_dir=str(tmp_path))

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


def test_youtube_sample_fallback_returns_only_youtube_records(monkeypatch):
    import etl.pipeline as pipeline

    def raise_missing_credentials(**_: Any) -> dict[str, list[dict[str, Any]]]:
        raise ExtractError("YOUTUBE_API_KEY is required for youtube source")

    monkeypatch.setattr(pipeline, "extract_youtube", raise_missing_credentials)

    raw, used_fallback = pipeline.extract_source("youtube", sample_fallback=True, limit=1)

    assert used_fallback is True
    assert {post["platform"] for post in raw["posts"]} == {"youtube"}
    assert {comment["platform"] for comment in raw["comments"]} == {"youtube"}


@pytest.mark.parametrize(
    "api_error",
    [
        ExtractError("YouTube quota exceeded"),
        requests.HTTPError("403 Client Error: Forbidden for url"),
    ],
)
def test_youtube_api_errors_fall_back_to_sample_data(monkeypatch, api_error):
    import etl.pipeline as pipeline

    def raise_api_error(**_: Any) -> dict[str, list[dict[str, Any]]]:
        raise api_error

    monkeypatch.setattr(pipeline, "extract_youtube", raise_api_error)

    raw, used_fallback = pipeline.extract_source(
        "youtube",
        query="Highlands Coffee",
        sample_fallback=True,
        limit=2,
    )

    assert used_fallback is True
    assert len(raw["posts"]) >= 500
    assert {post["platform"] for post in raw["posts"]} == {"youtube"}
    assert {comment["platform"] for comment in raw["comments"]} == {"youtube"}


def test_youtube_no_sample_fallback_raises_when_api_config_missing(monkeypatch):
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
            sample_fallback=False,
            limit=1,
        )


def test_run_pipeline_youtube_no_sample_fallback_raises_when_api_config_missing(
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
            sample_fallback=False,
            limit=1,
        )


def test_cli_run_youtube_no_sample_fallback_fails_when_api_config_missing(
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
            "--no-sample-fallback",
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
        ]
    )

    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert [call["source"] for call in calls] == ["youtube", "youtube"]
    assert [call["query"] for call in calls] == ["Highlands Coffee", "Phuc Long"]
    assert [call["page_id"] for call in calls] == [None, None]
    assert [call["limit"] for call in calls] == [7, 7]
    assert payload["runs"] == [
        {"source": "youtube", "query": "Highlands Coffee", "channel_id": None, "page_id": None},
        {"source": "youtube", "query": "Phuc Long", "channel_id": None, "page_id": None},
    ]
