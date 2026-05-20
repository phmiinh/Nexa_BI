"""Extractors for sample, local JSON, Facebook Graph API, and YouTube Data API."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import requests

from etl.sample import load_sample_data


class ExtractError(RuntimeError):
    """Raised when an external extractor fails."""


def _load_dotenv_if_available() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv()


def extract_sample() -> dict[str, list[dict[str, Any]]]:
    return load_sample_data()


def extract_json(path: str | Path) -> dict[str, list[dict[str, Any]]]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, list):
        return {"posts": payload, "comments": []}
    return {"posts": payload.get("posts", []), "comments": payload.get("comments", [])}


def extract_facebook(
    page_id: str,
    access_token: str | None = None,
    limit: int = 25,
    session: requests.Session | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Fetch a small Facebook page post/comment payload using Graph API.

    This is intentionally minimal for MVP usage. If credentials are missing, callers
    should use sample fallback rather than failing local demos.
    """

    _load_dotenv_if_available()
    token = access_token or os.getenv("FACEBOOK_ACCESS_TOKEN")
    if not token:
        raise ExtractError("FACEBOOK_ACCESS_TOKEN is required for facebook source")

    http = session or requests.Session()
    params = {
        "access_token": token,
        "limit": limit,
        "fields": (
            "id,message,created_time,full_picture,shares,"
            "reactions.summary(true),comments.limit(100).summary(true)"
        ),
    }
    response = http.get(f"https://graph.facebook.com/v19.0/{page_id}/posts", params=params, timeout=30)
    response.raise_for_status()
    posts: list[dict[str, Any]] = []
    comments: list[dict[str, Any]] = []
    for item in response.json().get("data", []):
        post_id = item.get("id", "")
        comment_block = item.get("comments", {})
        posts.append(
            {
                "id": post_id,
                "platform": "facebook",
                "page_id": page_id,
                "page_name": page_id,
                "message": item.get("message", ""),
                "created_time": item.get("created_time"),
                "content_type": "image" if item.get("full_picture") else "text",
                "reach": 0,
                "impressions": 0,
                "likes": item.get("reactions", {}).get("summary", {}).get("total_count", 0),
                "comments": comment_block.get("summary", {}).get("total_count", 0),
                "shares": item.get("shares", {}).get("count", 0),
            }
        )
        for comment in comment_block.get("data", []):
            comments.append(
                {
                    "id": comment.get("id"),
                    "post_id": post_id,
                    "platform": "facebook",
                    "author_id": comment.get("from", {}).get("id", ""),
                    "author_name": comment.get("from", {}).get("name", ""),
                    "text": comment.get("message", ""),
                    "created_time": comment.get("created_time"),
                }
            )
    return {"posts": posts, "comments": comments}


def extract_youtube(
    channel_id: str | None = None,
    query: str | None = None,
    api_key: str | None = None,
    limit: int = 25,
    session: requests.Session | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Fetch a small YouTube search/video payload using Data API v3."""

    _load_dotenv_if_available()
    key = api_key or os.getenv("YOUTUBE_API_KEY")
    if not key:
        raise ExtractError("YOUTUBE_API_KEY is required for youtube source")

    http = session or requests.Session()
    search_params = {
        "key": key,
        "part": "snippet",
        "type": "video",
        "maxResults": limit,
        "order": "date",
    }
    if channel_id:
        search_params["channelId"] = channel_id
    if query:
        search_params["q"] = query

    search_response = http.get(
        "https://www.googleapis.com/youtube/v3/search", params=search_params, timeout=30
    )
    search_response.raise_for_status()
    video_ids = [
        item.get("id", {}).get("videoId")
        for item in search_response.json().get("items", [])
        if item.get("id", {}).get("videoId")
    ]
    if not video_ids:
        return {"posts": [], "comments": []}

    video_response = http.get(
        "https://www.googleapis.com/youtube/v3/videos",
        params={"key": key, "part": "snippet,statistics", "id": ",".join(video_ids)},
        timeout=30,
    )
    video_response.raise_for_status()

    posts: list[dict[str, Any]] = []
    for item in video_response.json().get("items", []):
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        posts.append(
            {
                "id": item.get("id"),
                "platform": "youtube",
                "channel_id": snippet.get("channelId", channel_id or ""),
                "channel_title": snippet.get("channelTitle", ""),
                "title": snippet.get("title", ""),
                "publishedAt": snippet.get("publishedAt"),
                "content_type": "video",
                "views": stats.get("viewCount", 0),
                "likes": stats.get("likeCount", 0),
                "comment_count": stats.get("commentCount", 0),
                "shares": 0,
            }
        )
    return {"posts": posts, "comments": []}
