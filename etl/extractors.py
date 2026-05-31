"""Extractors for sample data, local JSON, optional Facebook, and YouTube Data API."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any
import unicodedata

import requests

from etl.sample import load_sample_data

LOGGER = logging.getLogger(__name__)


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
    comments_limit: int = 20,
    max_search_pages: int = 1,
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
    page_size = clamp_int(limit, 1, 50)
    search_pages = clamp_int(max_search_pages, 1, 12)
    per_video_comments = clamp_int(comments_limit, 0, 100)
    if channel_id:
        video_ids = fetch_youtube_channel_video_ids(
            http,
            key,
            channel_id,
            page_size=page_size,
            max_pages=search_pages,
        )
    else:
        video_ids = fetch_youtube_search_video_ids(
            http,
            key,
            query=query,
            page_size=page_size,
            max_pages=search_pages,
        )

    if not video_ids:
        return {"posts": [], "comments": []}

    posts: list[dict[str, Any]] = []
    comments: list[dict[str, Any]] = []
    for chunk in chunked(video_ids, 50):
        video_response = http.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={"key": key, "part": "snippet,statistics", "id": ",".join(chunk)},
            timeout=30,
        )
        raise_youtube_for_status(video_response, "videos.list")

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
            if per_video_comments:
                comments.extend(fetch_youtube_comments(http, key, video_id, limit=per_video_comments))
    return {"posts": posts, "comments": comments}


def clamp_int(value: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = minimum
    return max(minimum, min(parsed, maximum))


def chunked(values: list[str], size: int) -> list[list[str]]:
    return [values[index : index + size] for index in range(0, len(values), size)]


def fetch_youtube_channel_video_ids(
    session: requests.Session,
    api_key: str,
    channel_id: str,
    page_size: int,
    max_pages: int,
) -> list[str]:
    """Fetch video ids from a channel's uploads playlist.

    This is cheaper than search.list for official channels and keeps quota usage
    predictable when we need deeper history.
    """

    channel_response = session.get(
        "https://www.googleapis.com/youtube/v3/channels",
        params={"key": api_key, "part": "contentDetails", "id": channel_id},
        timeout=30,
    )
    raise_youtube_for_status(channel_response, "channels.list")
    items = channel_response.json().get("items", [])
    uploads_playlist_id = (
        items[0]
        .get("contentDetails", {})
        .get("relatedPlaylists", {})
        .get("uploads")
        if items
        else None
    )
    if not uploads_playlist_id:
        raise ExtractError(f"YouTube channel has no uploads playlist: {channel_id}")
    return fetch_youtube_playlist_video_ids(
        session,
        api_key,
        uploads_playlist_id,
        page_size=page_size,
        max_pages=max_pages,
    )


def fetch_youtube_playlist_video_ids(
    session: requests.Session,
    api_key: str,
    playlist_id: str,
    page_size: int,
    max_pages: int,
) -> list[str]:
    video_ids: list[str] = []
    seen_video_ids: set[str] = set()
    page_token: str | None = None
    for _ in range(max_pages):
        params = {
            "key": api_key,
            "part": "contentDetails",
            "playlistId": playlist_id,
            "maxResults": page_size,
        }
        if page_token:
            params["pageToken"] = page_token
        response = session.get(
            "https://www.googleapis.com/youtube/v3/playlistItems",
            params=params,
            timeout=30,
        )
        raise_youtube_for_status(response, "playlistItems.list")
        payload = response.json()
        for item in payload.get("items", []):
            video_id = item.get("contentDetails", {}).get("videoId")
            if video_id and video_id not in seen_video_ids:
                seen_video_ids.add(video_id)
                video_ids.append(video_id)
        page_token = payload.get("nextPageToken")
        if not page_token:
            break
    return video_ids


def fetch_youtube_search_video_ids(
    session: requests.Session,
    api_key: str,
    query: str | None,
    page_size: int,
    max_pages: int,
) -> list[str]:
    search_params = {
        "key": api_key,
        "part": "snippet",
        "type": "video",
        "maxResults": page_size,
        "order": "date",
    }
    if query:
        search_params["q"] = query

    video_ids: list[str] = []
    seen_video_ids: set[str] = set()
    page_token: str | None = None
    for _ in range(max_pages):
        params = dict(search_params)
        if page_token:
            params["pageToken"] = page_token
        response = session.get("https://www.googleapis.com/youtube/v3/search", params=params, timeout=30)
        raise_youtube_for_status(response, "search.list")
        payload = response.json()
        for item in payload.get("items", []):
            video_id = item.get("id", {}).get("videoId")
            if video_id and video_id not in seen_video_ids:
                seen_video_ids.add(video_id)
                video_ids.append(video_id)
        page_token = payload.get("nextPageToken")
        if not page_token:
            break
    return video_ids


def raise_youtube_for_status(response: requests.Response, operation: str) -> None:
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        status = getattr(response, "status_code", "request_error")
        reason = getattr(response, "reason", "YouTube API error")
        raise ExtractError(f"YouTube {operation} failed: {status} {reason}") from None


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
    except requests.RequestException as exc:
        status = getattr(exc.response, "status_code", "request_error")
        reason = getattr(exc.response, "reason", str(exc))
        LOGGER.warning("Skipping comments for YouTube video %s: %s %s", video_id, status, reason)
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
