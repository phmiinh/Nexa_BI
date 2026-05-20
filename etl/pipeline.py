"""End-to-end ETL orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from etl.extractors import ExtractError, extract_facebook, extract_json, extract_sample, extract_youtube
from etl.load import load_csv, load_sql
from etl.normalize import normalize_dataset
from etl.quality import QualityReport, check_quality


@dataclass
class PipelineResult:
    run_id: str
    source: str
    extracted_posts: int
    extracted_comments: int
    normalized_posts: int
    normalized_comments: int
    quality: QualityReport
    outputs: dict[str, Any]
    used_sample_fallback: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "run_id": self.run_id,
            "extracted_posts": self.extracted_posts,
            "extracted_comments": self.extracted_comments,
            "normalized_posts": self.normalized_posts,
            "normalized_comments": self.normalized_comments,
            "quality": self.quality.as_dict(),
            "outputs": self.outputs,
            "used_sample_fallback": self.used_sample_fallback,
        }


def extract_source(source: str, **kwargs: Any) -> tuple[dict[str, list[dict[str, Any]]], bool]:
    if source == "sample":
        return extract_sample(), False
    if source == "json":
        return extract_json(kwargs["input_path"]), False
    try:
        if source == "facebook":
            return extract_facebook(page_id=kwargs["page_id"], limit=kwargs.get("limit", 25)), False
        if source == "youtube":
            return extract_youtube(
                channel_id=kwargs.get("channel_id"),
                query=kwargs.get("query"),
                limit=kwargs.get("limit", 25),
            ), False
    except (ExtractError, KeyError):
        if kwargs.get("sample_fallback", True):
            return extract_sample(), True
        raise
    raise ValueError(f"unsupported source: {source}")


def run_pipeline(
    source: str = "sample",
    output_dir: str = "data/processed",
    database_url: str | None = None,
    fail_on_quality_error: bool = True,
    **extract_kwargs: Any,
) -> PipelineResult:
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    raw, used_fallback = extract_source(source, **extract_kwargs)
    actual_source = "sample" if used_fallback else source
    raw_outputs = write_raw_jsonl(raw, actual_source, run_id)
    tables = normalize_dataset(raw)
    quality = check_quality(tables["posts"], tables["comments"])
    if fail_on_quality_error and not quality.passed:
        raise ValueError(f"quality checks failed: {quality.errors}")

    outputs: dict[str, Any] = {"raw": raw_outputs, "csv": load_csv(tables, output_dir)}
    if database_url:
        outputs["sql"] = load_sql(tables, database_url)

    return PipelineResult(
        run_id=run_id,
        source=source,
        extracted_posts=len(raw.get("posts", [])),
        extracted_comments=len(raw.get("comments", [])),
        normalized_posts=len(tables["posts"]),
        normalized_comments=len(tables["comments"]),
        quality=quality,
        outputs=outputs,
        used_sample_fallback=used_fallback,
    )


def write_raw_jsonl(
    raw: dict[str, list[dict[str, Any]]], source: str, run_id: str, raw_root: str = "data/raw"
) -> dict[str, str]:
    output_dir = Path(raw_root) / source
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs: dict[str, str] = {}
    for name in ("posts", "comments"):
        target = output_dir / f"{name}_{run_id}.jsonl"
        with target.open("w", encoding="utf-8") as handle:
            for record in raw.get(name, []):
                handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
        outputs[name] = str(target)
    return outputs
