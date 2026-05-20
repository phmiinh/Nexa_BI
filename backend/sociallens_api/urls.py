from __future__ import annotations

from django.urls import path

from backend.sociallens_api import views

urlpatterns = [
    path("health/", views.health),
    path("api/v1/posts/", views.posts),
    path("api/v1/posts/<str:post_id>/", views.post_detail),
    path("api/v1/analytics/overview/", views.analytics_overview),
    path("api/v1/analytics/engagement/", views.analytics_engagement),
    path("api/v1/analytics/sentiment/", views.analytics_sentiment),
    path("api/v1/analytics/top-posts/", views.analytics_top_posts),
    path("api/v1/analytics/content-performance/", views.analytics_content_performance),
    path("api/v1/analytics/heatmap/", views.analytics_heatmap),
    path("api/v1/analytics/competitors/", views.analytics_competitors),
    path("api/v1/sync/status/", views.sync_status),
]
