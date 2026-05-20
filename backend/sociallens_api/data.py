from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from django.conf import settings


@dataclass(frozen=True)
class DataSource:
    name: str
    detail: str


class Repository:
    def __init__(self) -> None:
        self.processed_dir = Path(settings.SOCIALENS_PROCESSED_DIR)
        self.database_url = settings.SOCIALENS_DATABASE_URL
        self.source = DataSource("csv", str(self.processed_dir))

    def posts(self) -> pd.DataFrame:
        db = self._read_view("social_dw.vw_post_performance")
        if db is not None:
            db = db.rename(columns={"external_post_id": "post_id", "caption": "content_text"})
            return self._normalize_post_frame(db)

        frame = self._read_csv("posts.csv")
        return self._normalize_post_frame(frame)

    def comments(self) -> pd.DataFrame:
        return self._read_csv("comments.csv")

    def overview(self) -> dict[str, Any]:
        db = self._read_view("social_dw.vw_executive_overview")
        if db is not None and not db.empty:
            row = clean_record(db.iloc[0].to_dict())
            row["source"] = self.source.name
            return row

        posts = self.posts()
        return {
            "total_posts": int(len(posts)),
            "total_reach": int(posts["reach"].sum()),
            "total_impressions": int(posts["impressions"].sum()),
            "total_engagement": int(posts["engagement_count"].sum()),
            "avg_engagement_rate": safe_round(posts["engagement_rate"].mean()),
            "avg_virality_score": safe_round(posts["virality_score"].mean()),
            "date_from": min_or_none(posts, "date"),
            "date_to": max_or_none(posts, "date"),
            "source": self.source.name,
        }

    def engagement(self) -> list[dict[str, Any]]:
        db = self._read_view("social_dw.vw_daily_engagement")
        if db is not None:
            return records(db)

        posts = self.posts()
        grouped = (
            posts.groupby(["date", "platform"], dropna=False)
            .agg(
                post_count=("post_id", "count"),
                total_reach=("reach", "sum"),
                total_impressions=("impressions", "sum"),
                total_engagement=("engagement_count", "sum"),
                avg_engagement_rate=("engagement_rate", "mean"),
                avg_virality_score=("virality_score", "mean"),
            )
            .reset_index()
            .rename(columns={"date": "full_date", "platform": "platform_name"})
            .sort_values(["full_date", "platform_name"])
        )
        return records(grouped)

    def sentiment(self) -> list[dict[str, Any]]:
        db = self._read_view("social_dw.vw_sentiment_trend")
        if db is not None:
            return records(db)

        comments = self.comments()
        posts = self.posts()[["post_id", "page_name"]].drop_duplicates()
        comments = comments.merge(posts, on="post_id", how="left")
        grouped = comments.groupby(["date", "platform", "page_name"], dropna=False)
        frame = grouped.agg(
            comment_count=("comment_id", "count"),
            positive_count=("sentiment_label", lambda s: int((s == "positive").sum())),
            neutral_count=("sentiment_label", lambda s: int((s == "neutral").sum())),
            negative_count=("sentiment_label", lambda s: int((s == "negative").sum())),
            avg_sentiment_score=("sentiment_score", "mean"),
        ).reset_index()
        frame["positive_pct"] = pct(frame["positive_count"], frame["comment_count"])
        frame["negative_pct"] = pct(frame["negative_count"], frame["comment_count"])
        frame = frame.rename(columns={"date": "full_date", "platform": "platform_name"})
        return records(frame.sort_values(["full_date", "platform_name", "page_name"]))

    def content_performance(self) -> list[dict[str, Any]]:
        db = self._read_view("social_dw.vw_content_performance")
        if db is not None:
            return records(db)

        posts = self.posts()
        posts["is_competitor"] = posts["page_name"].map(is_competitor)
        frame = (
            posts.groupby(["platform", "content_type", "is_competitor"], dropna=False)
            .agg(
                post_count=("post_id", "count"),
                total_reach=("reach", "sum"),
                total_impressions=("impressions", "sum"),
                total_engagement=("engagement_count", "sum"),
                avg_engagement_rate=("engagement_rate", "mean"),
                avg_virality_score=("virality_score", "mean"),
            )
            .reset_index()
            .rename(columns={"platform": "platform_name"})
            .sort_values(["platform_name", "content_type", "is_competitor"])
        )
        return records(frame)

    def heatmap(self) -> list[dict[str, Any]]:
        db = self._read_view("social_dw.vw_posting_time_heatmap")
        if db is not None:
            return records(db)

        posts = self.posts()
        frame = (
            posts.groupby(["day_of_week", "hour", "platform"], dropna=False)
            .agg(
                post_count=("post_id", "count"),
                avg_engagement_rate=("engagement_rate", "mean"),
                total_engagement=("engagement_count", "sum"),
            )
            .reset_index()
            .rename(columns={"hour": "hour_of_day", "platform": "platform_name"})
            .sort_values(["day_of_week", "hour_of_day", "platform_name"])
        )
        frame["day_name"] = frame["day_of_week"]
        return records(frame)

    def competitors(self) -> list[dict[str, Any]]:
        db = self._read_view("social_dw.vw_competitor_benchmark")
        if db is not None:
            return records(db)

        posts = self.posts()
        posts["is_competitor"] = posts["page_name"].map(is_competitor)
        frame = (
            posts.groupby(["platform", "page_name", "is_competitor"], dropna=False)
            .agg(
                post_count=("post_id", "count"),
                total_reach=("reach", "sum"),
                total_engagement=("engagement_count", "sum"),
                avg_engagement_rate=("engagement_rate", "mean"),
                avg_virality_score=("virality_score", "mean"),
            )
            .reset_index()
            .rename(columns={"platform": "platform_name"})
            .sort_values(["platform_name", "is_competitor", "page_name"])
        )
        frame["industry"] = "F&B"
        return records(frame)

    def top_posts(self, limit: int = 10) -> list[dict[str, Any]]:
        db = self._read_view("social_dw.vw_viral_posts")
        if db is not None:
            return records(db.head(limit))

        posts = self.posts()
        columns = [
            "post_id",
            "platform",
            "page_name",
            "content_type",
            "date",
            "reach",
            "engagement_count",
            "engagement_rate",
            "virality_score",
            "content_text",
        ]
        frame = posts[columns].rename(
            columns={
                "platform": "platform_name",
                "date": "full_date",
                "content_text": "caption",
            }
        )
        frame = frame.sort_values(
            ["virality_score", "engagement_count"], ascending=[False, False], na_position="last"
        )
        return records(frame.head(limit))

    def sync_status(self) -> dict[str, Any]:
        db = self._query(
            """
            SELECT run_id, source, started_at, finished_at, status,
                   extracted_posts, extracted_comments, loaded_posts, loaded_comments, error_message
            FROM social_dw.etl_runs
            ORDER BY finished_at DESC, run_id DESC
            LIMIT 1
            """
        )
        if db is not None and not db.empty:
            row = clean_record(db.iloc[0].to_dict())
            row["source_type"] = self.source.name
            return row

        posts_path = self.processed_dir / "posts.csv"
        comments_path = self.processed_dir / "comments.csv"
        return {
            "status": "available" if posts_path.exists() else "missing",
            "source": "processed_csv",
            "source_type": "csv",
            "posts_path": str(posts_path),
            "comments_path": str(comments_path),
            "posts_modified_at": modified_at(posts_path),
            "comments_modified_at": modified_at(comments_path),
        }

    def _normalize_post_frame(self, frame: pd.DataFrame) -> pd.DataFrame:
        frame = frame.copy()
        if "platform_name" in frame.columns and "platform" not in frame.columns:
            frame["platform"] = frame["platform_name"]
        if "caption" in frame.columns and "content_text" not in frame.columns:
            frame["content_text"] = frame["caption"]
        if "comments" in frame.columns and "comments_count" not in frame.columns:
            frame["comments_count"] = frame["comments"]
        if "full_date" in frame.columns and "date" not in frame.columns:
            frame["date"] = frame["full_date"]
        if "hour_of_day" in frame.columns and "hour" not in frame.columns:
            frame["hour"] = frame["hour_of_day"]
        if "engagement_count" not in frame.columns:
            saves = frame["saves"] if "saves" in frame.columns else 0
            frame["engagement_count"] = frame["likes"] + frame["comments_count"] + frame["shares"] + saves
        return frame

    def _read_csv(self, filename: str) -> pd.DataFrame:
        path = self.processed_dir / filename
        self.source = DataSource("csv", str(path))
        if not path.exists():
            raise FileNotFoundError(f"Processed data file not found: {path}")
        return pd.read_csv(path)

    def _read_view(self, name: str) -> pd.DataFrame | None:
        frame = self._query(f"SELECT * FROM {name}")
        if frame is not None:
            self.source = DataSource("warehouse", name)
        return frame

    def _query(self, sql: str) -> pd.DataFrame | None:
        if not self.database_url:
            return None
        try:
            from sqlalchemy import create_engine

            engine = create_engine(self.database_url)
            with engine.connect() as connection:
                return pd.read_sql_query(sql, connection)
        except Exception:
            return None


def clean_record(row: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in row.items():
        if pd.isna(value):
            result[key] = None
        elif hasattr(value, "isoformat"):
            result[key] = value.isoformat()
        elif hasattr(value, "item"):
            result[key] = value.item()
        else:
            result[key] = value
    return result


def records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    return [clean_record(row) for row in frame.to_dict("records")]


def safe_round(value: Any) -> float | None:
    if pd.isna(value):
        return None
    return round(float(value), 4)


def pct(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    return (numerator / denominator.where(denominator != 0) * 100).round(2)


def min_or_none(frame: pd.DataFrame, column: str) -> Any:
    return None if frame.empty else clean_record({"value": frame[column].min()})["value"]


def max_or_none(frame: pd.DataFrame, column: str) -> Any:
    return None if frame.empty else clean_record({"value": frame[column].max()})["value"]


def is_competitor(page_name: Any) -> bool:
    return str(page_name).strip().lower() in {"phuc long", "the coffee house"}


def modified_at(path: Path) -> str | None:
    if not path.exists():
        return None
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()
