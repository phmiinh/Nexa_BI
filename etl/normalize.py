"""Normalize raw social platform payloads into analytics-ready tables."""

from __future__ import annotations

from typing import Any

import pandas as pd

from etl.sentiment import analyze_sentiment


POST_COLUMNS = [
    "post_id",
    "platform",
    "page_id",
    "page_name",
    "content_text",
    "content_type",
    "posted_at",
    "date",
    "hour",
    "day_of_week",
    "reach",
    "impressions",
    "likes",
    "comments_count",
    "shares",
    "engagement_rate",
    "virality_score",
]

COMMENT_COLUMNS = [
    "comment_id",
    "post_id",
    "platform",
    "author_id",
    "author_name",
    "comment_text",
    "commented_at",
    "date",
    "hour",
    "sentiment_label",
    "sentiment_score",
]


def _as_int(value: Any) -> int:
    if value is None or value == "":
        return 0
    try:
        return max(0, int(float(value)))
    except (TypeError, ValueError):
        return 0


def _first_present(row: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return value
    return default


def _timestamp(value: Any) -> pd.Timestamp:
    if value in (None, ""):
        return pd.NaT
    return pd.to_datetime(value, utc=True, errors="coerce").tz_convert("Asia/Ho_Chi_Minh")


def _content_type(row: dict[str, Any]) -> str:
    raw = str(_first_present(row, "content_type", "type", "media_type", default="")).lower()
    if raw in {"video", "image", "story", "reel", "text", "short", "livestream"}:
        return "reel" if raw == "short" else raw
    if _first_present(row, "video_id", "youtube_id"):
        return "video"
    if _first_present(row, "picture", "full_picture", "thumbnail"):
        return "image"
    return "text"


def normalize_posts(raw_posts: list[dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for raw in raw_posts:
        platform = str(_first_present(raw, "platform", default="unknown")).lower()
        post_id = str(_first_present(raw, "post_id", "id", "external_id", "video_id", default="")).strip()
        posted_at = _timestamp(_first_present(raw, "posted_at", "created_time", "publishedAt"))
        reach = _as_int(_first_present(raw, "reach", "view_count", "views"))
        impressions = _as_int(_first_present(raw, "impressions", default=reach))
        likes = _as_int(_first_present(raw, "likes", "like_count"))
        comments_count = _as_int(_first_present(raw, "comments_count", "comments", "comment_count"))
        shares = _as_int(_first_present(raw, "shares", "share_count"))
        engagement_rate = round((likes + comments_count + shares) / reach * 100, 4) if reach else None
        virality_score = round(shares / reach * 100, 4) if reach else None

        rows.append(
            {
                "post_id": post_id,
                "platform": platform,
                "page_id": str(_first_present(raw, "page_id", "channel_id", default="")),
                "page_name": str(_first_present(raw, "page_name", "channel_title", "from_name", default="")),
                "content_text": str(_first_present(raw, "content_text", "message", "caption", "title", default="")),
                "content_type": _content_type(raw),
                "posted_at": posted_at,
                "date": posted_at.date().isoformat() if not pd.isna(posted_at) else "",
                "hour": int(posted_at.hour) if not pd.isna(posted_at) else None,
                "day_of_week": posted_at.day_name() if not pd.isna(posted_at) else "",
                "reach": reach,
                "impressions": impressions,
                "likes": likes,
                "comments_count": comments_count,
                "shares": shares,
                "engagement_rate": engagement_rate,
                "virality_score": virality_score,
            }
        )

    return pd.DataFrame(rows, columns=POST_COLUMNS).drop_duplicates("post_id")


def normalize_comments(raw_comments: list[dict[str, Any]]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for raw in raw_comments:
        commented_at = _timestamp(_first_present(raw, "commented_at", "created_time", "publishedAt"))
        text = str(_first_present(raw, "comment_text", "text", "message", default=""))
        sentiment = analyze_sentiment(text)
        rows.append(
            {
                "comment_id": str(_first_present(raw, "comment_id", "id", default="")).strip(),
                "post_id": str(_first_present(raw, "post_id", "parent_id", default="")).strip(),
                "platform": str(_first_present(raw, "platform", default="unknown")).lower(),
                "author_id": str(_first_present(raw, "author_id", default="")),
                "author_name": str(_first_present(raw, "author_name", default="")),
                "comment_text": text,
                "commented_at": commented_at,
                "date": commented_at.date().isoformat() if not pd.isna(commented_at) else "",
                "hour": int(commented_at.hour) if not pd.isna(commented_at) else None,
                "sentiment_label": sentiment.label,
                "sentiment_score": sentiment.score,
            }
        )

    return pd.DataFrame(rows, columns=COMMENT_COLUMNS).drop_duplicates("comment_id")


def normalize_dataset(raw: dict[str, list[dict[str, Any]]]) -> dict[str, pd.DataFrame]:
    return {
        "posts": normalize_posts(raw.get("posts", [])),
        "comments": normalize_comments(raw.get("comments", [])),
    }
