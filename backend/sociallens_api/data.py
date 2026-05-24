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
            db = db.rename(
                columns={
                    "post_id": "warehouse_post_id",
                    "external_post_id": "post_id",
                    "caption": "content_text",
                }
            )
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

    def _legacy_insights(self) -> dict[str, Any]:
        overview = self.overview()
        top_posts = self.top_posts(1)
        content = self.content_performance()
        sentiment = self.sentiment()

        insight_rows: list[dict[str, Any]] = []
        source = self.source.name

        total_posts = int(overview.get("total_posts") or 0)
        total_engagement = int(overview.get("total_engagement") or 0)
        avg_engagement_rate = overview.get("avg_engagement_rate")
        if total_posts:
            insight_rows.append(
                {
                    "type": "overview",
                    "title": "Tổng quan hiệu suất",
                    "message": (
                        f"Hệ thống ghi nhận {total_posts} bài viết với {total_engagement} lượt tương tác; "
                        f"tỷ lệ tương tác trung bình là {format_metric(avg_engagement_rate)}%."
                    ),
                }
            )

        if top_posts:
            post = top_posts[0]
            insight_rows.append(
                {
                    "type": "top_post",
                    "title": "Bài viết nổi bật",
                    "message": (
                        f"Bài viết nổi bật nhất thuộc {post.get('page_name') or 'không rõ trang'} "
                        f"trên {post.get('platform_name') or post.get('platform') or 'không rõ nền tảng'} "
                        f"với điểm lan truyền {format_metric(post.get('virality_score'))}."
                    ),
                }
            )

        best_content = max(
            content,
            key=lambda row: (
                float(row.get("avg_engagement_rate") or 0),
                int(row.get("total_engagement") or 0),
            ),
            default=None,
        )
        if best_content:
            insight_rows.append(
                {
                    "type": "content",
                    "title": "Định dạng nội dung hiệu quả",
                    "message": (
                        f"Nội dung {best_content.get('content_type') or 'không rõ loại'} "
                        f"trên {best_content.get('platform_name') or 'không rõ nền tảng'} "
                        f"đang có tỷ lệ tương tác trung bình {format_metric(best_content.get('avg_engagement_rate'))}%."
                    ),
                }
            )

        sentiment_totals = {
            "positive": sum(int(row.get("positive_count") or 0) for row in sentiment),
            "neutral": sum(int(row.get("neutral_count") or 0) for row in sentiment),
            "negative": sum(int(row.get("negative_count") or 0) for row in sentiment),
        }
        if sum(sentiment_totals.values()):
            dominant = max(sentiment_totals, key=sentiment_totals.get)
            labels = {"positive": "tích cực", "neutral": "trung lập", "negative": "tiêu cực"}
            insight_rows.append(
                {
                    "type": "sentiment",
                    "title": "Sắc thái bình luận",
                    "message": (
                        f"Bình luận {labels[dominant]} chiếm tỷ trọng lớn nhất "
                        f"với {sentiment_totals[dominant]} lượt ghi nhận."
                    ),
                }
            )

        return {
            "source": source,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "freshness": {
                "dataFrom": overview.get("date_from"),
                "dataThrough": overview.get("date_to"),
                "generatedAt": datetime.now(timezone.utc).isoformat(),
                "status": "fresh" if total_posts else "unknown",
            },
            "source_confidence": source_confidence(source, "success" if total_posts else "missing"),
            "insights": insight_rows,
        }

    def insights(self) -> dict[str, Any]:
        overview = self.overview()
        top_posts = self.top_posts(1)
        content = self.content_performance()
        sentiment = self.sentiment()

        insight_rows: list[dict[str, Any]] = []
        source = self.source.name
        total_posts = int(overview.get("total_posts") or 0)
        total_engagement = int(overview.get("total_engagement") or 0)
        avg_engagement_rate = overview.get("avg_engagement_rate")
        if total_posts:
            insight_rows.append(
                {
                    "type": "overview",
                    "title": "Tổng quan hiệu suất",
                    "message": (
                        f"Hệ thống ghi nhận {total_posts} video với {total_engagement} lượt tương tác; "
                        f"tỷ lệ tương tác trung bình là {format_metric(avg_engagement_rate)}%."
                    ),
                }
            )

        if top_posts:
            post = top_posts[0]
            insight_rows.append(
                {
                    "type": "top_post",
                    "title": "Video nổi bật",
                    "message": (
                        f"Video nổi bật nhất thuộc {post.get('page_name') or 'không rõ kênh'} "
                        f"trên {post.get('platform_name') or post.get('platform') or 'không rõ nền tảng'} "
                        f"với điểm lan truyền {format_metric(post.get('virality_score'))}."
                    ),
                }
            )

        best_content = max(
            content,
            key=lambda row: (
                float(row.get("avg_engagement_rate") or 0),
                int(row.get("total_engagement") or 0),
            ),
            default=None,
        )
        if best_content:
            insight_rows.append(
                {
                    "type": "content",
                    "title": "Định dạng nội dung hiệu quả",
                    "message": (
                        f"Nội dung {best_content.get('content_type') or 'không rõ loại'} "
                        f"trên {best_content.get('platform_name') or 'không rõ nền tảng'} "
                        f"đang có tỷ lệ tương tác trung bình "
                        f"{format_metric(best_content.get('avg_engagement_rate'))}%."
                    ),
                }
            )

        sentiment_totals = {
            "positive": sum(int(row.get("positive_count") or 0) for row in sentiment),
            "neutral": sum(int(row.get("neutral_count") or 0) for row in sentiment),
            "negative": sum(int(row.get("negative_count") or 0) for row in sentiment),
        }
        if sum(sentiment_totals.values()):
            dominant = max(sentiment_totals, key=sentiment_totals.get)
            labels = {"positive": "tích cực", "neutral": "trung lập", "negative": "tiêu cực"}
            insight_rows.append(
                {
                    "type": "sentiment",
                    "title": "Sắc thái bình luận",
                    "message": (
                        f"Bình luận {labels[dominant]} chiếm tỷ trọng lớn nhất "
                        f"với {sentiment_totals[dominant]} lượt ghi nhận."
                    ),
                }
            )

        return {
            "source": source,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "freshness": {
                "dataFrom": overview.get("date_from"),
                "dataThrough": overview.get("date_to"),
                "generatedAt": datetime.now(timezone.utc).isoformat(),
                "status": "fresh" if total_posts else "unknown",
            },
            "source_confidence": source_confidence(source, "success" if total_posts else "missing"),
            "insights": insight_rows,
        }

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
        if db is not None:
            row = clean_record(db.iloc[0].to_dict()) if not db.empty else {"status": "available", "source": "warehouse"}
            row["source_type"] = "warehouse"
            row.update(self._warehouse_current_state() or {"counts": {"posts": None, "comments": None}, "platforms": []})
            row["source_confidence"] = source_confidence("warehouse", row.get("status"))
            return row

        posts_path = self.processed_dir / "posts.csv"
        comments_path = self.processed_dir / "comments.csv"
        fallback_state = self._csv_current_state(posts_path, comments_path)
        return {
            "status": "available" if posts_path.exists() else "missing",
            "source": "processed_csv",
            "source_type": "csv",
            "posts_path": str(posts_path),
            "comments_path": str(comments_path),
            "posts_modified_at": modified_at(posts_path),
            "comments_modified_at": modified_at(comments_path),
            **fallback_state,
            "source_confidence": source_confidence("csv", "available" if posts_path.exists() else "missing"),
        }

    def _warehouse_current_state(self) -> dict[str, Any] | None:
        frame = self._query(
            """
            SELECT
                (SELECT count(*) FROM social_dw.fact_post) AS post_count,
                (SELECT count(*) FROM social_dw.fact_sentiment) AS comment_count,
                (
                    SELECT min(dt.full_date)
                    FROM social_dw.fact_post fp
                    JOIN social_dw.dim_time dt ON dt.time_id = fp.time_id
                ) AS data_from,
                (
                    SELECT max(dt.full_date)
                    FROM social_dw.fact_post fp
                    JOIN social_dw.dim_time dt ON dt.time_id = fp.time_id
                ) AS data_through,
                (
                    SELECT string_agg(platform_name, ',' ORDER BY platform_name)
                    FROM (
                        SELECT DISTINCT dp.platform_name
                        FROM social_dw.fact_post fp
                        JOIN social_dw.dim_platform dp ON dp.platform_id = fp.platform_id
                    ) loaded_platforms
                ) AS platforms
            """
        )
        if frame is None:
            return None
        if frame.empty:
            return {
                "counts": {"posts": 0, "comments": 0},
                "platforms": [],
                "freshness": {
                    "dataFrom": None,
                    "dataThrough": None,
                    "generatedAt": datetime.now(timezone.utc).isoformat(),
                    "status": "unknown",
                },
            }

        row = clean_record(frame.iloc[0].to_dict())
        platforms = [value for value in str(row.get("platforms") or "").split(",") if value]
        post_count = int(row.get("post_count") or 0)
        return {
            "counts": {
                "posts": post_count,
                "comments": int(row.get("comment_count") or 0),
            },
            "platforms": platforms,
            "freshness": {
                "dataFrom": row.get("data_from"),
                "dataThrough": row.get("data_through"),
                "generatedAt": datetime.now(timezone.utc).isoformat(),
                "status": "fresh" if post_count else "unknown",
            },
        }

    def _csv_current_state(self, posts_path: Path, comments_path: Path) -> dict[str, Any]:
        posts = pd.read_csv(posts_path) if posts_path.exists() else pd.DataFrame()
        comments = pd.read_csv(comments_path) if comments_path.exists() else pd.DataFrame()
        platforms = []
        if "platform" in posts.columns:
            platforms = sorted(posts["platform"].dropna().astype(str).str.lower().unique().tolist())
        return {
            "counts": {"posts": int(len(posts)), "comments": int(len(comments))},
            "platforms": platforms,
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

            engine = create_engine(self.database_url, connect_args={"connect_timeout": 3})
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


def format_metric(value: Any) -> str:
    if value is None or pd.isna(value):
        return "0"
    return f"{float(value):.2f}".rstrip("0").rstrip(".")


def source_confidence(source_type: str, status: Any) -> dict[str, Any]:
    if source_type == "warehouse" and str(status).lower() in {"success", "available", "completed"}:
        return {
            "level": "high",
            "score": 0.92,
            "reason": "Current warehouse data is loaded from real YouTube API with no sample fallback.",
            "detail": "Current warehouse data is loaded from real YouTube API with no sample fallback.",
        }
    if source_type == "warehouse":
        return {
            "level": "medium",
            "score": 0.7,
            "reason": "Warehouse is reachable, but the latest sync run is not marked successful.",
            "detail": "Warehouse is reachable, but the latest sync run is not marked successful.",
        }
    if str(status).lower() == "available":
        return {
            "level": "medium",
            "score": 0.7,
            "reason": "Warehouse is unavailable; API is using the latest processed CSV data.",
            "detail": "Warehouse is unavailable; API is using the latest processed CSV data.",
        }
    return {
        "level": "low",
        "score": 0.3,
        "reason": "No warehouse or processed CSV data is available.",
        "detail": "No warehouse or processed CSV data is available.",
    }


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
