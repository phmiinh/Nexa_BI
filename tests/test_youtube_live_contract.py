from __future__ import annotations

import os

import pytest

from etl.extractors import ExtractError, extract_youtube

pytestmark = pytest.mark.live_youtube


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv()


def _first_channel_id() -> str | None:
    configured = os.getenv("YOUTUBE_LIVE_CHANNEL_ID") or os.getenv("YOUTUBE_CHANNEL_IDS", "")
    return next((value.strip() for value in configured.split(",") if value.strip()), None)


def test_youtube_official_channel_live_contract_uses_uploads_playlist():
    if os.getenv("RUN_YOUTUBE_LIVE_TESTS") != "1":
        pytest.skip("Set RUN_YOUTUBE_LIVE_TESTS=1 to run live YouTube contract tests.")

    _load_dotenv()
    api_key = os.getenv("YOUTUBE_API_KEY")
    channel_id = _first_channel_id()
    if not api_key or not channel_id:
        pytest.skip("YOUTUBE_API_KEY and YOUTUBE_CHANNEL_IDS or YOUTUBE_LIVE_CHANNEL_ID are required.")

    try:
        payload = extract_youtube(
            channel_id=channel_id,
            api_key=api_key,
            limit=1,
            comments_limit=0,
            max_search_pages=1,
        )
    except ExtractError as exc:
        message = str(exc)
        if "401" in message or "403" in message:
            pytest.skip(f"YouTube API credentials/quota are not available for live contract: {message}")
        raise

    assert len(payload["posts"]) == 1
    assert payload["comments"] == []
    post = payload["posts"][0]
    assert post["platform"] == "youtube"
    assert post["channel_id"] == channel_id
    assert post["source_confidence"] == "official_channel"
    assert post["id"]
    assert post["publishedAt"]
