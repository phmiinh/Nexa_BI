from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPORT_VIEWS = [
    "vw_executive_overview",
    "vw_daily_engagement",
    "vw_sentiment_trend",
    "vw_content_performance",
    "vw_competitor_benchmark",
    "vw_posting_time_heatmap",
    "vw_viral_posts",
]


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    assert reader.fieldnames, f"{path} must have a header row"
    return rows


def test_dashboard_exports_exist_and_are_parseable():
    export_dir = ROOT / "dashboard" / "exports"

    for view in EXPORT_VIEWS:
        csv_path = export_dir / f"{view}.csv"
        json_path = export_dir / f"{view}.json"

        assert csv_path.is_file(), f"missing CSV export: {csv_path}"
        assert json_path.is_file(), f"missing JSON export: {json_path}"
        assert read_csv_rows(csv_path), f"{csv_path} must contain at least one data row"

        with json_path.open(encoding="utf-8") as handle:
            payload = json.load(handle)

        assert isinstance(payload, list), f"{json_path} must contain a JSON array"
        assert payload, f"{json_path} must contain at least one object"
        assert all(isinstance(item, dict) for item in payload), f"{json_path} rows must be objects"


def test_processed_csv_outputs_are_youtube_only():
    processed_dir = ROOT / "data" / "processed"

    for filename in ["posts.csv", "comments.csv"]:
        path = processed_dir / filename
        rows = read_csv_rows(path)
        platforms = {row["platform"].strip().lower() for row in rows if row.get("platform")}

        assert rows, f"{path} must contain at least one data row"
        assert "platform" in rows[0], f"{path} must include a platform column"
        assert platforms == {"youtube"}


def test_bi_insight_docs_and_notebook_guides_are_present():
    required_artifacts = [
        ROOT / "docs" / "Data_Dictionary.md",
        ROOT / "docs" / "ETL_Process.md",
        ROOT / "docs" / "Quality_Checks.md",
        ROOT / "docs" / "Report_Outline.md",
        ROOT / "notebooks" / "README.md",
    ]

    for path in required_artifacts:
        assert path.is_file(), f"missing final-delivery artifact: {path}"
        assert path.stat().st_size > 0, f"{path} must not be empty"
