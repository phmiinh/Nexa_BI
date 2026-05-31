"""Load normalized ETL outputs to CSV files and the PostgreSQL star schema."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


def load_csv(tables: dict[str, pd.DataFrame], output_dir: str | Path) -> dict[str, str]:
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    outputs: dict[str, str] = {}
    for name, frame in tables.items():
        target = path / f"{name}.csv"
        frame.to_csv(target, index=False, encoding="utf-8")
        outputs[name] = str(target)
    return outputs


def load_sql(
    tables: dict[str, pd.DataFrame],
    database_url: str,
    if_exists: str = "replace",
    run_source: str = "etl.cli",
) -> dict[str, int]:
    try:
        from sqlalchemy import create_engine, text
    except ImportError as exc:
        raise RuntimeError("sqlalchemy is required when --database-url is used") from exc

    engine = create_engine(database_url)
    if engine.dialect.name != "postgresql":
        counts: dict[str, int] = {}
        with engine.begin() as connection:
            for name, frame in tables.items():
                table_name = f"social_{name}"
                frame.to_sql(table_name, connection, if_exists=if_exists, index=False)
                counts[table_name] = len(frame)
        return counts

    ensure_schema(engine)
    posts = tables["posts"].copy()
    comments = tables["comments"].copy()

    with engine.begin() as connection:
        platform_ids = upsert_platforms(connection, posts)
        content_type_ids = upsert_content_types(connection, posts)
        page_ids = upsert_pages(connection, posts, platform_ids)
        time_ids = upsert_times(connection, posts, comments)
        post_ids = upsert_posts(connection, posts, platform_ids, content_type_ids, page_ids, time_ids)
        sentiment_count = upsert_sentiments(connection, comments, platform_ids, time_ids, post_ids)

        connection.execute(
            text(
                """
                INSERT INTO social_dw.etl_runs (
                    source, extracted_posts, extracted_comments, loaded_posts, loaded_comments, status
                )
                VALUES (:source, :extracted_posts, :extracted_comments, :loaded_posts, :loaded_comments, 'success')
                """
            ),
            {
                "source": run_source,
                "extracted_posts": len(posts),
                "extracted_comments": len(comments),
                "loaded_posts": len(posts),
                "loaded_comments": sentiment_count,
            },
        )

    return {
        "social_dw.fact_post": len(posts),
        "social_dw.fact_sentiment": sentiment_count,
    }


def ensure_schema(engine: Any) -> None:
    root = Path(__file__).resolve().parents[1]
    schema_files = [
        root / "warehouse" / "schema" / "001_schema.sql",
        root / "warehouse" / "schema" / "002_indexes.sql",
        root / "warehouse" / "schema" / "003_views.sql",
    ]
    with engine.begin() as connection:
        for sql_file in schema_files:
            connection.exec_driver_sql(sql_file.read_text(encoding="utf-8"))


def time_key(value: Any) -> int:
    ts = pd.to_datetime(value, utc=True, errors="coerce")
    if pd.isna(ts):
        ts = pd.Timestamp.utcnow()
    return int(ts.strftime("%Y%m%d%H%M%S"))


def time_payload(value: Any) -> dict[str, Any]:
    ts = pd.to_datetime(value, utc=True, errors="coerce")
    if pd.isna(ts):
        ts = pd.Timestamp.utcnow()
    local = ts.tz_convert("Asia/Ho_Chi_Minh")
    return {
        "time_id": time_key(ts),
        "full_date": local.date(),
        "full_timestamp": ts.to_pydatetime(),
        "hour_of_day": int(local.hour),
        "day_of_week": int(local.isoweekday()),
        "day_name": local.day_name(),
        "week_of_year": int(local.isocalendar().week),
        "month_of_year": int(local.month),
        "month_name": local.month_name(),
        "quarter_of_year": int(local.quarter),
        "calendar_year": int(local.year),
        "is_weekend": bool(local.isoweekday() >= 6),
    }


def upsert_platforms(connection: Any, posts: pd.DataFrame) -> dict[str, int]:
    from sqlalchemy import text

    platforms = sorted(set(posts["platform"].dropna().astype(str).str.lower()))
    for platform in platforms:
        platform_type = "video_platform" if platform == "youtube" else "social_network"
        connection.execute(
            text(
                """
                INSERT INTO social_dw.dim_platform (platform_name, platform_type, api_source)
                VALUES (:platform_name, :platform_type, :api_source)
                ON CONFLICT (platform_name) DO NOTHING
                """
            ),
            {
                "platform_name": platform,
                "platform_type": platform_type,
                "api_source": "sample/API",
            },
        )
    rows = connection.execute(
        text("SELECT platform_id, platform_name FROM social_dw.dim_platform")
    ).mappings()
    return {row["platform_name"]: row["platform_id"] for row in rows}


def upsert_content_types(connection: Any, posts: pd.DataFrame) -> dict[str, int]:
    from sqlalchemy import text

    for content_type in sorted(set(posts["content_type"].dropna().astype(str).str.lower())):
        category = "video" if content_type in {"video", "reel", "short", "livestream"} else "post"
        connection.execute(
            text(
                """
                INSERT INTO social_dw.dim_content_type (type_name, type_category)
                VALUES (:type_name, :type_category)
                ON CONFLICT (type_name) DO NOTHING
                """
            ),
            {"type_name": content_type, "type_category": category},
        )
    rows = connection.execute(
        text("SELECT content_type_id, type_name FROM social_dw.dim_content_type")
    ).mappings()
    return {row["type_name"]: row["content_type_id"] for row in rows}


def is_competitor(page_name: str) -> bool:
    normalized = page_name.strip().lower()
    return normalized in {
        "phuc long",
        "the coffee house",
        "cong caphe",
        "starbucksvietnam",
        "starbucks vietnam",
        "gong cha vietnam",
        "cheese coffee",
    } or normalized.startswith(("trung", "starbucks", "koi"))


def upsert_pages(
    connection: Any, posts: pd.DataFrame, platform_ids: dict[str, int]
) -> dict[tuple[str, str], int]:
    from sqlalchemy import text

    page_frame = posts[["platform", "page_id", "page_name"]].drop_duplicates()
    for row in page_frame.to_dict("records"):
        platform = str(row["platform"]).lower()
        external_page_id = str(row["page_id"] or row["page_name"])
        page_name = str(row["page_name"] or external_page_id)
        connection.execute(
            text(
                """
                INSERT INTO social_dw.dim_page (
                    platform_id, external_page_id, page_name, industry, country_code,
                    is_competitor, follower_count
                )
                VALUES (
                    :platform_id, :external_page_id, :page_name, 'F&B', 'VN',
                    :is_competitor, 0
                )
                ON CONFLICT (platform_id, external_page_id) DO UPDATE SET
                    page_name = EXCLUDED.page_name,
                    is_competitor = EXCLUDED.is_competitor,
                    updated_at = now()
                """
            ),
            {
                "platform_id": platform_ids[platform],
                "external_page_id": external_page_id,
                "page_name": page_name,
                "is_competitor": is_competitor(page_name),
            },
        )
    rows = connection.execute(
        text(
            """
            SELECT page_id, platform_id, external_page_id
            FROM social_dw.dim_page
            """
        )
    ).mappings()
    platform_by_id = {value: key for key, value in platform_ids.items()}
    return {
        (platform_by_id[row["platform_id"]], row["external_page_id"]): row["page_id"]
        for row in rows
    }


def upsert_times(connection: Any, posts: pd.DataFrame, comments: pd.DataFrame) -> dict[int, int]:
    from sqlalchemy import text

    values = list(posts["posted_at"]) + list(comments["commented_at"])
    payloads: dict[int, dict[str, Any]] = {}
    for value in values:
        payload = time_payload(value)
        if payload["time_id"] in payloads:
            continue
        payloads[payload["time_id"]] = payload
    if payloads:
        connection.execute(
            text(
                """
                INSERT INTO social_dw.dim_time (
                    time_id, full_date, full_timestamp, hour_of_day, day_of_week,
                    day_name, week_of_year, month_of_year, month_name,
                    quarter_of_year, calendar_year, is_weekend
                )
                VALUES (
                    :time_id, :full_date, :full_timestamp, :hour_of_day, :day_of_week,
                    :day_name, :week_of_year, :month_of_year, :month_name,
                    :quarter_of_year, :calendar_year, :is_weekend
                )
                ON CONFLICT (time_id) DO NOTHING
                """
            ),
            list(payloads.values()),
        )
    return {key: key for key in payloads}


def upsert_posts(
    connection: Any,
    posts: pd.DataFrame,
    platform_ids: dict[str, int],
    content_type_ids: dict[str, int],
    page_ids: dict[tuple[str, str], int],
    time_ids: dict[int, int],
) -> dict[tuple[str, str], int]:
    from sqlalchemy import text

    payloads: list[dict[str, Any]] = []
    for row in posts.to_dict("records"):
        platform = str(row["platform"]).lower()
        external_page_id = str(row["page_id"] or row["page_name"])
        timestamp_key = time_key(row["posted_at"])
        payloads.append(
            {
                "external_post_id": row["post_id"],
                "platform_id": platform_ids[platform],
                "time_id": time_ids[timestamp_key],
                "content_type_id": content_type_ids[str(row["content_type"]).lower()],
                "page_id": page_ids[(platform, external_page_id)],
                "caption": row["content_text"],
                "reach": int(row["reach"]),
                "impressions": int(row["impressions"]),
                "likes": int(row["likes"]),
                "comments": int(row["comments_count"]),
                "shares": int(row["shares"]),
            }
        )
    if payloads:
        connection.execute(
            text(
                """
                INSERT INTO social_dw.fact_post (
                    external_post_id, platform_id, time_id, content_type_id, page_id,
                    caption, reach, impressions, likes, comments, shares, saves
                )
                VALUES (
                    :external_post_id, :platform_id, :time_id, :content_type_id, :page_id,
                    :caption, :reach, :impressions, :likes, :comments, :shares, 0
                )
                ON CONFLICT (platform_id, external_post_id) DO UPDATE SET
                    time_id = EXCLUDED.time_id,
                    content_type_id = EXCLUDED.content_type_id,
                    page_id = EXCLUDED.page_id,
                    caption = EXCLUDED.caption,
                    reach = EXCLUDED.reach,
                    impressions = EXCLUDED.impressions,
                    likes = EXCLUDED.likes,
                    comments = EXCLUDED.comments,
                    shares = EXCLUDED.shares,
                    loaded_at = now()
                """
            ),
            payloads,
        )
    rows = connection.execute(
        text(
            """
            SELECT fp.post_id, fp.external_post_id, dp.platform_name
            FROM social_dw.fact_post fp
            JOIN social_dw.dim_platform dp ON dp.platform_id = fp.platform_id
            """
        )
    ).mappings()
    return {(row["platform_name"], row["external_post_id"]): row["post_id"] for row in rows}


def upsert_sentiments(
    connection: Any,
    comments: pd.DataFrame,
    platform_ids: dict[str, int],
    time_ids: dict[int, int],
    post_ids: dict[tuple[str, str], int],
) -> int:
    from sqlalchemy import text

    payloads: list[dict[str, Any]] = []
    for row in comments.to_dict("records"):
        platform = str(row["platform"]).lower()
        post_key = (platform, str(row["post_id"]))
        if post_key not in post_ids:
            continue
        timestamp_key = time_key(row["commented_at"])
        payloads.append(
            {
                "external_comment_id": row["comment_id"],
                "post_id": post_ids[post_key],
                "platform_id": platform_ids[platform],
                "time_id": time_ids[timestamp_key],
                "sentiment_label": row["sentiment_label"],
                "sentiment_score": float(row["sentiment_score"]),
                "comment_text": row["comment_text"],
            }
        )
    if payloads:
        connection.execute(
            text(
                """
                INSERT INTO social_dw.fact_sentiment (
                    external_comment_id, post_id, platform_id, time_id,
                    sentiment_label, sentiment_score, comment_text
                )
                VALUES (
                    :external_comment_id, :post_id, :platform_id, :time_id,
                    :sentiment_label, :sentiment_score, :comment_text
                )
                ON CONFLICT (platform_id, external_comment_id) DO UPDATE SET
                    post_id = EXCLUDED.post_id,
                    time_id = EXCLUDED.time_id,
                    sentiment_label = EXCLUDED.sentiment_label,
                    sentiment_score = EXCLUDED.sentiment_score,
                    comment_text = EXCLUDED.comment_text,
                    loaded_at = now()
                """
            ),
            payloads,
        )
    return len(payloads)
