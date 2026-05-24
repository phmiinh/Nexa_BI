"""Extractors for sample data, local JSON, optional Facebook, and YouTube Data API."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
import unicodedata

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

    This is intentionally minimal and optional. The MVP production data source is YouTube.
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
    if not channel_id and not query:
        raise ExtractError("YOUTUBE_CHANNEL_IDS or YOUTUBE_QUERIES is required for youtube source")

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
    comments: list[dict[str, Any]] = []
    for item in video_response.json().get("items", []):
        snippet = item.get("snippet", {})
        if query and not matches_youtube_query(snippet, query):
            continue
        stats = item.get("statistics", {})
        video_id = item.get("id")
        posts.append(
            {
                "id": video_id,
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
                "source_query": query or "",
                "source_confidence": "official_channel" if channel_id else "query_filtered",
            }
        )
        comments.extend(fetch_youtube_comments(http, key, video_id))
    return {"posts": posts, "comments": comments}


def matches_youtube_query(snippet: dict[str, Any], query: str) -> bool:
    """Keep query-search results that clearly match the requested brand/topic."""

    normalized_query = normalize_search_text(query)
    if not normalized_query:
        return True

    haystack = normalize_search_text(
        " ".join(
            str(snippet.get(key, ""))
            for key in ("channelTitle", "title", "description")
        )
    )

    required_phrases = [
        "highlands coffee",
        "phuc long",
        "the coffee house",
    ]
    phrase = next((item for item in required_phrases if item in normalized_query), "")
    if phrase:
        if phrase not in haystack:
            return False
        if phrase == "the coffee house":
            return any(
                marker in haystack
                for marker in (
                    "vietnam",
                    "viet nam",
                    "ha noi",
                    "ho chi minh",
                    "sai gon",
                    "saigon",
                    "phan van tri",
                    "hao nam",
                    "hoan kiem",
                    "fomo",
                    "combo 99k",
                    "highlands coffee",
                )
            )
        return True

    if normalized_query in haystack:
        return True

    tokens = [token for token in normalized_query.split() if len(token) >= 4]
    if not tokens:
        return True
    matched = sum(1 for token in tokens if token in haystack)
    return matched >= max(1, min(len(tokens), 2))


def normalize_search_text(value: str) -> str:
    text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return " ".join(text.lower().split())


def fetch_youtube_comments(
    session: requests.Session, api_key: str, video_id: str | None, limit: int = 20
) -> list[dict[str, Any]]:
    if not video_id:
        return []
    try:
        response = session.get(
            "https://www.googleapis.com/youtube/v3/commentThreads",
            params={
                "key": api_key,
                "part": "snippet",
                "videoId": video_id,
                "maxResults": limit,
                "order": "relevance",
                "textFormat": "plainText",
            },
            timeout=30,
        )
        response.raise_for_status()
    except requests.RequestException:
        return []

    comments: list[dict[str, Any]] = []
    for item in response.json().get("items", []):
        top = item.get("snippet", {}).get("topLevelComment", {})
        snippet = top.get("snippet", {})
        comments.append(
            {
                "id": top.get("id") or item.get("id"),
                "post_id": video_id,
                "platform": "youtube",
                "author_id": snippet.get("authorChannelId", {}).get("value", ""),
                "author_name": snippet.get("authorDisplayName", ""),
                "text": snippet.get("textDisplay", ""),
                "created_time": snippet.get("publishedAt"),
            }
        )
    return comments
