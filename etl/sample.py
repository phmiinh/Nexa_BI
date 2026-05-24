"""Deterministic YouTube/F&B sample data for local development and tests."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any


PAGES = [
    ("highlands", "Highlands Coffee", False, 2400000),
    ("phuc_long", "Phuc Long", True, 1700000),
    ("the_coffee_house", "The Coffee House", True, 1500000),
]

PLATFORMS = ["youtube"]
CONTENT_TYPES = ["video", "short", "livestream"]
POSITIVE_COMMENTS = [
    "Ca phe ngon, minh rat thich uu dai nay",
    "Video hay va noi dung huu ich",
    "Nhan vien phuc vu tot, se quay lai",
]
NEGATIVE_COMMENTS = [
    "Giao hang cham va app bi loi, can cai thien",
    "Gia hoi dat, trai nghiem hom nay kem",
    "Do uong khong ngon nhu mong doi",
]
NEUTRAL_COMMENTS = [
    "Da nhan thong tin",
    "Minh se ghe cua hang vao cuoi tuan",
    "Bai viet nay noi ve chuong trinh moi",
]


def load_sample_data() -> dict[str, list[dict[str, Any]]]:
    """Return deterministic F&B social data with enough rows for BI visuals."""

    posts: list[dict[str, Any]] = []
    comments: list[dict[str, Any]] = []
    start = datetime(2025, 11, 20, 2, 0, tzinfo=timezone.utc)
    post_index = 0

    for day in range(180):
        for platform in PLATFORMS:
            for page_id, page_name, is_competitor, followers in PAGES:
                post_index += 1
                published = start + timedelta(days=day, hours=(post_index * 3) % 17)
                content_type = CONTENT_TYPES[post_index % len(CONTENT_TYPES)]
                platform_boost = 1.25 if platform == "youtube" else 1.0
                competitor_boost = 0.9 if is_competitor else 1.15
                reach = int((2600 + day * 18 + (post_index % 13) * 210) * platform_boost * competitor_boost)
                likes = int(reach * (0.035 + (post_index % 5) * 0.004))
                comment_count = int(reach * (0.006 + (post_index % 4) * 0.001))
                shares = int(reach * (0.004 + (post_index % 6) * 0.001))
                post_id = f"{platform}_{page_id}_{day:03d}"
                topic = "combo ca phe sua da" if content_type != "video" else "hau truong rang xay"
                posts.append(
                    {
                        "id": post_id,
                        "platform": platform,
                        "page_id": page_id,
                        "page_name": page_name,
                        "message": f"{page_name} chia se {topic} ngay {day + 1}",
                        "created_time": published.isoformat().replace("+00:00", "Z"),
                        "content_type": content_type,
                        "reach": reach,
                        "impressions": int(reach * 1.22),
                        "likes": likes,
                        "comments": comment_count,
                        "shares": shares,
                        "follower_count": followers + day * (90 if not is_competitor else 55),
                        "is_competitor": is_competitor,
                    }
                )

                comment_texts = [
                    POSITIVE_COMMENTS[(post_index + day) % len(POSITIVE_COMMENTS)],
                    NEGATIVE_COMMENTS[(post_index + day) % len(NEGATIVE_COMMENTS)]
                    if post_index % 5 == 0
                    else NEUTRAL_COMMENTS[(post_index + day) % len(NEUTRAL_COMMENTS)],
                ]
                for comment_offset, text in enumerate(comment_texts):
                    comments.append(
                        {
                            "id": f"cmt_{post_id}_{comment_offset}",
                            "post_id": post_id,
                            "platform": platform,
                            "author_id": f"user_{(post_index + comment_offset) % 97}",
                            "author_name": f"User {(post_index + comment_offset) % 97}",
                            "text": text,
                            "created_time": (
                                published + timedelta(minutes=12 + comment_offset * 7)
                            ).isoformat().replace("+00:00", "Z"),
                        }
                    )

    return {"posts": posts, "comments": comments}
