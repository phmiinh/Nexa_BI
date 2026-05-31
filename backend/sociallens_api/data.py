from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from functools import lru_cache
import logging
from typing import Any

import pandas as pd
from django.conf import settings

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class DataSource:
    name: str
    detail: str


class WarehouseUnavailable(RuntimeError):
    """Raised when the canonical PostgreSQL warehouse cannot serve data."""


class Repository:
    def __init__(self) -> None:
        self.database_url = settings.SOCIALENS_DATABASE_URL
        self.source = DataSource("warehouse", "social_dw")

    def posts(self) -> pd.DataFrame:
        db = self._read_view("social_dw.vw_post_performance")
        db = db.rename(
            columns={
                "post_id": "warehouse_post_id",
                "external_post_id": "post_id",
                "caption": "content_text",
            }
        )
        return self._normalize_post_frame(db)

    def comments(self) -> pd.DataFrame:
        return self._query("SELECT * FROM social_dw.fact_sentiment")

    def overview(self) -> dict[str, Any]:
        db = self._read_view("social_dw.vw_executive_overview")
        if not db.empty:
            row = clean_record(db.iloc[0].to_dict())
            row["source"] = self.source.name
            return row
        return {
            "total_posts": 0,
            "total_reach": 0,
            "total_impressions": 0,
            "total_engagement": 0,
            "avg_engagement_rate": None,
            "avg_virality_score": None,
            "date_from": None,
            "date_to": None,
            "source": self.source.name,
        }

    def engagement(self, limit: int | None = None) -> list[dict[str, Any]]:
        frame = self._read_view(
            "social_dw.vw_daily_engagement",
            order_by="full_date DESC, platform_name",
            limit=limit,
        )
        return records(frame.sort_values(["full_date", "platform_name"]))

    def sentiment(self, limit: int | None = None) -> list[dict[str, Any]]:
        frame = self._read_view(
            "social_dw.vw_sentiment_trend",
            order_by="full_date DESC, platform_name, page_name",
            limit=limit,
        )
        return records(frame.sort_values(["full_date", "platform_name", "page_name"]))

    def content_performance(self) -> list[dict[str, Any]]:
        return records(self._read_view("social_dw.vw_content_performance"))

    def heatmap(self) -> list[dict[str, Any]]:
        return records(self._read_view("social_dw.vw_posting_time_heatmap"))

    def competitors(self) -> list[dict[str, Any]]:
        return records(self._read_view("social_dw.vw_competitor_benchmark"))

    def top_posts(self, limit: int = 10) -> list[dict[str, Any]]:
        db = self._read_view(
            "social_dw.vw_viral_posts",
            order_by="virality_score DESC NULLS LAST, engagement_count DESC NULLS LAST",
            limit=limit,
        )
        return records(db)

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
        row = clean_record(db.iloc[0].to_dict()) if not db.empty else {"status": "available", "source": "warehouse"}
        row["source_type"] = "warehouse"
        row.update(self._warehouse_current_state())
        row["source_confidence"] = source_confidence("warehouse", row.get("status"))
        return row

    def _warehouse_current_state(self) -> dict[str, Any]:
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

    def _read_view(
        self,
        name: str,
        order_by: str | None = None,
        limit: int | None = None,
    ) -> pd.DataFrame:
        sql = f"SELECT * FROM {name}"
        if order_by:
            sql = f"{sql} ORDER BY {order_by}"
        params: dict[str, Any] = {}
        if limit:
            sql = f"{sql} LIMIT :limit"
            params["limit"] = int(limit)
        frame = self._query(sql, params or None)
        self.source = DataSource("warehouse", name)
        return frame

    def _query(self, sql: str, params: dict[str, Any] | None = None) -> pd.DataFrame:
        if not self.database_url:
            raise WarehouseUnavailable("SOCIALENS_DATABASE_URL or DATABASE_URL is required")
        try:
            from sqlalchemy import text

            engine = warehouse_engine(self.database_url)
            with engine.connect() as connection:
                return pd.read_sql_query(text(sql), connection, params=params)
        except Exception as exc:
            LOGGER.exception("Warehouse query failed")
            raise WarehouseUnavailable(f"warehouse query failed: {exc}") from exc


@lru_cache(maxsize=4)
def warehouse_engine(database_url: str) -> Any:
    from sqlalchemy import create_engine

    return create_engine(database_url, connect_args={"connect_timeout": 3}, pool_pre_ping=True)


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
            "reason": "Current warehouse data is loaded from real YouTube API without sample data.",
            "detail": "Current warehouse data is loaded from real YouTube API without sample data.",
        }
    if source_type == "warehouse":
        return {
            "level": "medium",
            "score": 0.7,
            "reason": "Warehouse is reachable, but the latest sync run is not marked successful.",
            "detail": "Warehouse is reachable, but the latest sync run is not marked successful.",
        }
    return {
        "level": "low",
        "score": 0.3,
        "reason": "Warehouse data is unavailable.",
        "detail": "Warehouse data is unavailable.",
    }


def pct(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    return (numerator / denominator.where(denominator != 0) * 100).round(2)


def min_or_none(frame: pd.DataFrame, column: str) -> Any:
    return None if frame.empty else clean_record({"value": frame[column].min()})["value"]


def max_or_none(frame: pd.DataFrame, column: str) -> Any:
    return None if frame.empty else clean_record({"value": frame[column].max()})["value"]


def is_competitor(page_name: Any) -> bool:
    normalized = str(page_name).strip().lower()
    return normalized in {
        "phuc long",
        "the coffee house",
        "cong caphe",
        "starbucksvietnam",
        "starbucks vietnam",
        "gong cha vietnam",
        "cheese coffee",
    } or normalized.startswith(("trung", "starbucks", "koi"))
