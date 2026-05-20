"""Command-line entrypoint for the SocialLens BI ETL MVP."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

import pandas as pd

from etl.load import load_sql
from etl.pipeline import run_pipeline
from etl.quality import check_quality


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
    run_parser.add_argument("--sources", default="facebook,youtube,sample")
    run_parser.add_argument("--output-dir", default="data/processed")
    run_parser.add_argument("--database-url")
    run_parser.add_argument("--limit", type=int, default=25)
    run_parser.add_argument("--allow-quality-errors", action="store_true")

    load_parser = subparsers.add_parser("load", help="Load existing processed CSV files into warehouse")
    load_parser.add_argument("--input-dir", default="data/processed")
    load_parser.add_argument("--database-url", required=True)

    quality_parser = subparsers.add_parser("quality", help="Run processed CSV quality checks")
    quality_parser.add_argument("--input-dir", default="data/processed")
    quality_parser.add_argument("--database-url")

    export_parser = subparsers.add_parser("export", help="Export warehouse views for Power BI/Next fallback")
    export_parser.add_argument("--database-url", required=True)
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
    for source in [item.strip() for item in args.sources.split(",") if item.strip()]:
        source_args = argparse.Namespace(
            source=source,
            input_path=None,
            output_dir=args.output_dir,
            database_url=args.database_url,
            page_id=None,
            channel_id=None,
            query=None,
            limit=args.limit,
            no_sample_fallback=False,
            allow_quality_errors=args.allow_quality_errors,
        )
        results.append(run_single_source(source_args))
    return {"runs": results}


def load_existing_csv(input_dir: str, database_url: str) -> dict[str, Any]:
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
            result = load_existing_csv(args.input_dir, args.database_url)
        elif args.command == "quality":
            result = quality_existing_csv(args.input_dir)
        elif args.command == "export":
            result = {"exports": export_views(args.database_url, args.output_dir)}
        else:
            result = run_single_source(args)
    except Exception as exc:
        logging.error("ETL failed: %s", exc)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
