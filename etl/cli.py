"""Command-line entrypoint for the SocialLens BI ETL MVP."""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

import pandas as pd

from etl.load import load_csv, load_sql
from etl.normalize import normalize_dataset
from etl.pipeline import run_pipeline
from etl.quality import check_quality

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv()


def add_pipeline_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--source", choices=["sample", "json", "facebook", "youtube"], default="sample")
    parser.add_argument("--input-path", help="JSON file for --source json")
    parser.add_argument("--output-dir", default="data/processed")
    parser.add_argument("--database-url", help="SQLAlchemy URL")
    parser.add_argument("--page-id", help="Facebook page id")
    parser.add_argument("--channel-id", help="YouTube channel id")
    parser.add_argument("--query", help="YouTube search query")
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--no-sample-fallback", action="store_true")
    parser.add_argument("--allow-quality-errors", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run SocialLens BI ETL")
    parser.add_argument("--log-level", default="INFO")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run extract, transform, quality, CSV, and optional warehouse load")
    run_parser.add_argument("--sources", default="youtube")
    run_parser.add_argument("--output-dir", default="data/processed")
    run_parser.add_argument("--database-url")
    run_parser.add_argument("--limit", type=int, default=25)
    run_parser.add_argument("--no-sample-fallback", action="store_true")
    run_parser.add_argument("--allow-quality-errors", action="store_true")

    load_parser = subparsers.add_parser("load", help="Load existing processed CSV files into warehouse")
    load_parser.add_argument("--input-dir", default="data/processed")
    load_parser.add_argument("--database-url")

    quality_parser = subparsers.add_parser("quality", help="Run processed CSV quality checks")
    quality_parser.add_argument("--input-dir", default="data/processed")
    quality_parser.add_argument("--database-url")

    export_parser = subparsers.add_parser("export", help="Export warehouse views for Power BI/Next fallback")
    export_parser.add_argument("--database-url")
    export_parser.add_argument("--output-dir", default="dashboard/exports")

    legacy_parser = subparsers.add_parser("_legacy", help=argparse.SUPPRESS)
    add_pipeline_args(legacy_parser)
    return parser


def run_single_source(args: argparse.Namespace) -> dict[str, Any]:
    return run_pipeline(
        source=args.source,
        input_path=getattr(args, "input_path", None),
        output_dir=args.output_dir,
        database_url=args.database_url,
        page_id=getattr(args, "page_id", None),
        channel_id=getattr(args, "channel_id", None),
        query=getattr(args, "query", None),
        limit=args.limit,
        sample_fallback=not getattr(args, "no_sample_fallback", False),
        fail_on_quality_error=not args.allow_quality_errors,
    ).as_dict()


def run_many(args: argparse.Namespace) -> dict[str, Any]:
    results = []
    database_url = args.database_url
    for source in [item.strip() for item in args.sources.split(",") if item.strip()]:
        for source_args in expand_source_args(source, args, database_url):
            results.append(run_single_source(source_args))
    payload: dict[str, Any] = {"runs": results}
    if should_consolidate(results):
        payload["consolidated"] = consolidate_raw_outputs(
            results,
            args.output_dir,
            fail_on_quality_error=not args.allow_quality_errors,
        )
    return payload


def should_consolidate(results: list[dict[str, Any]]) -> bool:
    if len(results) <= 1:
        return False
    return any(result.get("outputs", {}).get("raw") for result in results)


def consolidate_raw_outputs(
    results: list[dict[str, Any]], output_dir: str, fail_on_quality_error: bool = True
) -> dict[str, Any]:
    raw: dict[str, list[dict[str, Any]]] = {"posts": [], "comments": []}
    for result in results:
        raw_paths = result.get("outputs", {}).get("raw", {})
        for name in ("posts", "comments"):
            path_value = raw_paths.get(name)
            if not path_value:
                continue
            path = Path(path_value)
            if not path.exists():
                continue
            with path.open("r", encoding="utf-8") as handle:
                raw[name].extend(json.loads(line) for line in handle if line.strip())

    tables = normalize_dataset(raw)
    quality = check_quality(tables["posts"], tables["comments"])
    if fail_on_quality_error and not quality.passed:
        raise ValueError(f"consolidated quality checks failed: {quality.errors}")

    return {
        "normalized_posts": len(tables["posts"]),
        "normalized_comments": len(tables["comments"]),
        "quality": quality.as_dict(),
        "csv": load_csv(tables, output_dir),
    }


def split_env_list(name: str) -> list[str]:
    return [item.strip() for item in os.getenv(name, "").split(",") if item.strip()]


def expand_source_args(
    source: str, args: argparse.Namespace, database_url: str | None
) -> list[argparse.Namespace]:
    base = {
        "source": source,
        "input_path": None,
        "output_dir": args.output_dir,
        "database_url": database_url,
        "page_id": None,
        "channel_id": None,
        "query": None,
        "limit": args.limit,
        "no_sample_fallback": getattr(args, "no_sample_fallback", False),
        "allow_quality_errors": args.allow_quality_errors,
    }
    if source != "youtube":
        return [argparse.Namespace(**base)]

    channel_ids = split_env_list("YOUTUBE_CHANNEL_IDS")
    queries = split_env_list("YOUTUBE_QUERIES")
    expanded: list[argparse.Namespace] = []
    for channel_id in channel_ids:
        expanded.append(argparse.Namespace(**{**base, "channel_id": channel_id}))
    for query in queries:
        expanded.append(argparse.Namespace(**{**base, "query": query}))
    return expanded or [argparse.Namespace(**base)]


def load_existing_csv(input_dir: str, database_url: str) -> dict[str, Any]:
    if not database_url:
        raise ValueError("database_url is required for warehouse load")
    path = Path(input_dir)
    posts_path = path / "posts.csv"
    comments_path = path / "comments.csv"
    if not posts_path.exists() or not comments_path.exists():
        raise FileNotFoundError("posts.csv and comments.csv are required before load")
    tables = {
        "posts": pd.read_csv(posts_path, parse_dates=["posted_at"]),
        "comments": pd.read_csv(comments_path, parse_dates=["commented_at"]),
    }
    return {"sql": load_sql(tables, database_url)}


def quality_existing_csv(input_dir: str) -> dict[str, Any]:
    path = Path(input_dir)
    posts = pd.read_csv(path / "posts.csv")
    comments = pd.read_csv(path / "comments.csv")
    report = check_quality(posts, comments)
    return report.as_dict()


def export_views(database_url: str, output_dir: str) -> dict[str, str]:
    if not database_url:
        raise ValueError("database_url is required for warehouse export")
    from sqlalchemy import create_engine

    views = [
        "vw_executive_overview",
        "vw_daily_engagement",
        "vw_sentiment_trend",
        "vw_content_performance",
        "vw_competitor_benchmark",
        "vw_posting_time_heatmap",
        "vw_viral_posts",
    ]
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    engine = create_engine(database_url)
    exports: dict[str, str] = {}
    with engine.begin() as connection:
        for view in views:
            frame = pd.read_sql(f"SELECT * FROM social_dw.{view}", connection)
            csv_path = output / f"{view}.csv"
            json_path = output / f"{view}.json"
            frame.to_csv(csv_path, index=False, encoding="utf-8")
            frame.to_json(json_path, orient="records", force_ascii=False, date_format="iso")
            exports[view] = str(csv_path)
    return exports


def normalize_legacy_argv(argv: list[str] | None) -> list[str] | None:
    if argv is None:
        argv = sys.argv[1:]
    commands = {"run", "load", "quality", "export"}
    if argv and argv[0] in commands:
        return argv
    return ["_legacy", *argv]


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(normalize_legacy_argv(argv))
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(levelname)s %(message)s",
    )

    try:
        if args.command == "run":
            result = run_many(args)
        elif args.command == "load":
            result = load_existing_csv(args.input_dir, args.database_url or os.getenv("DATABASE_URL"))
        elif args.command == "quality":
            result = quality_existing_csv(args.input_dir)
        elif args.command == "export":
            result = {"exports": export_views(args.database_url or os.getenv("DATABASE_URL"), args.output_dir)}
        else:
            result = run_single_source(args)
    except Exception as exc:
        logging.error("ETL failed: %s", exc)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
