"""Quality checks for SocialLens normalized ETL data."""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class QualityReport:
    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, object]:
        return {"passed": self.passed, "errors": self.errors, "warnings": self.warnings}


def check_quality(posts: pd.DataFrame, comments: pd.DataFrame) -> QualityReport:
    errors: list[str] = []
    warnings: list[str] = []

    required_post_columns = {"post_id", "platform", "posted_at", "reach", "engagement_rate"}
    required_comment_columns = {"comment_id", "post_id", "comment_text", "sentiment_label", "sentiment_score"}
    missing_posts = required_post_columns - set(posts.columns)
    missing_comments = required_comment_columns - set(comments.columns)
    if missing_posts:
        errors.append(f"posts missing columns: {sorted(missing_posts)}")
    if missing_comments:
        errors.append(f"comments missing columns: {sorted(missing_comments)}")

    if not posts.empty:
        if posts["post_id"].isna().any() or (posts["post_id"].astype(str).str.strip() == "").any():
            errors.append("posts contain empty post_id")
        if posts["post_id"].duplicated().any():
            errors.append("posts contain duplicate post_id")
        if (posts[["reach", "impressions", "likes", "comments_count", "shares"]] < 0).any().any():
            errors.append("posts contain negative metric values")
        if posts["posted_at"].isna().any():
            warnings.append("some posts have invalid posted_at")
        high_engagement = posts["engagement_rate"] > 100
        if high_engagement.any():
            warnings.append(f"{int(high_engagement.sum())} posts have engagement_rate > 100")
    else:
        warnings.append("posts table is empty")

    if not comments.empty:
        if comments["comment_id"].isna().any() or (comments["comment_id"].astype(str).str.strip() == "").any():
            errors.append("comments contain empty comment_id")
        if comments["comment_id"].duplicated().any():
            errors.append("comments contain duplicate comment_id")
        orphan_mask = ~comments["post_id"].isin(set(posts["post_id"])) if "post_id" in posts else pd.Series([], dtype=bool)
        if orphan_mask.any():
            warnings.append(f"{int(orphan_mask.sum())} comments reference missing posts")
        bad_labels = ~comments["sentiment_label"].isin({"positive", "neutral", "negative"})
        if bad_labels.any():
            errors.append("comments contain invalid sentiment_label")
    else:
        warnings.append("comments table is empty")

    return QualityReport(passed=not errors, errors=errors, warnings=warnings)
