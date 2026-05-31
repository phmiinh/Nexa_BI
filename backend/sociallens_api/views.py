from __future__ import annotations

import logging
from typing import Any

from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_GET

from backend.sociallens_api.data import Repository, WarehouseUnavailable, records

LOGGER = logging.getLogger(__name__)


def ok(payload: Any, status: int = 200) -> JsonResponse:
    return JsonResponse(payload, status=status, json_dumps_params={"ensure_ascii": False})


def warehouse_error(exc: WarehouseUnavailable) -> JsonResponse:
    LOGGER.warning("Warehouse unavailable for API request", exc_info=exc.__cause__ is not None)
    return ok(
        {
            "detail": "Warehouse unavailable",
            "source_type": "warehouse",
            "error_code": "WAREHOUSE_UNAVAILABLE",
        },
        status=503,
    )


def parse_limit(request: HttpRequest, default: int = 10, maximum: int = 100) -> int:
    try:
        value = int(request.GET.get("limit", default))
    except (TypeError, ValueError):
        value = default
    return max(1, min(value, maximum))


@require_GET
def health(_: HttpRequest) -> JsonResponse:
    return ok({"status": "ok", "service": "sociallens-api"})


@require_GET
def posts(request: HttpRequest) -> JsonResponse:
    try:
        repo = Repository()
        frame = repo.posts()
        platform = request.GET.get("platform")
        if platform:
            frame = frame[frame["platform"].astype(str).str.lower() == platform.lower()]
        page = request.GET.get("page")
        if page:
            frame = frame[frame["page_name"].astype(str).str.lower() == page.lower()]
        frame = frame.sort_values(["date", "post_id"], ascending=[False, True]).head(parse_limit(request, 50, 500))
        return ok({"count": len(frame), "source": repo.source.name, "results": records(frame)})
    except WarehouseUnavailable as exc:
        return warehouse_error(exc)


@require_GET
def post_detail(_: HttpRequest, post_id: str) -> JsonResponse:
    try:
        repo = Repository()
        frame = repo.posts()
        match = frame[frame["post_id"].astype(str) == post_id]
        if match.empty:
            return ok({"detail": "Not found"}, status=404)
        return ok({"source": repo.source.name, "result": records(match.head(1))[0]})
    except WarehouseUnavailable as exc:
        return warehouse_error(exc)


@require_GET
def analytics_overview(_: HttpRequest) -> JsonResponse:
    try:
        return ok(Repository().overview())
    except WarehouseUnavailable as exc:
        return warehouse_error(exc)


@require_GET
def analytics_engagement(request: HttpRequest) -> JsonResponse:
    try:
        repo = Repository()
        return ok({"source": repo.source.name, "results": repo.engagement(limit=parse_limit(request, 120, 500))})
    except WarehouseUnavailable as exc:
        return warehouse_error(exc)


@require_GET
def analytics_sentiment(request: HttpRequest) -> JsonResponse:
    try:
        repo = Repository()
        return ok({"source": repo.source.name, "results": repo.sentiment(limit=parse_limit(request, 120, 500))})
    except WarehouseUnavailable as exc:
        return warehouse_error(exc)


@require_GET
def analytics_top_posts(request: HttpRequest) -> JsonResponse:
    try:
        repo = Repository()
        return ok({"source": repo.source.name, "results": repo.top_posts(parse_limit(request))})
    except WarehouseUnavailable as exc:
        return warehouse_error(exc)


@require_GET
def analytics_content_performance(_: HttpRequest) -> JsonResponse:
    try:
        repo = Repository()
        return ok({"source": repo.source.name, "results": repo.content_performance()})
    except WarehouseUnavailable as exc:
        return warehouse_error(exc)


@require_GET
def analytics_heatmap(_: HttpRequest) -> JsonResponse:
    try:
        repo = Repository()
        return ok({"source": repo.source.name, "results": repo.heatmap()})
    except WarehouseUnavailable as exc:
        return warehouse_error(exc)


@require_GET
def analytics_competitors(_: HttpRequest) -> JsonResponse:
    try:
        repo = Repository()
        return ok({"source": repo.source.name, "results": repo.competitors()})
    except WarehouseUnavailable as exc:
        return warehouse_error(exc)


@require_GET
def analytics_insights(_: HttpRequest) -> JsonResponse:
    try:
        return ok(Repository().insights())
    except WarehouseUnavailable as exc:
        return warehouse_error(exc)


@require_GET
def sync_status(_: HttpRequest) -> JsonResponse:
    try:
        return ok(Repository().sync_status())
    except WarehouseUnavailable as exc:
        return warehouse_error(exc)
