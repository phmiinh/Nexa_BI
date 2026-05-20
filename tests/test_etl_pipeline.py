from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

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
