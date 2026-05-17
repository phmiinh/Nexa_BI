# 🏗️ DESIGN.md — SocialLens BI
> Technical Design & Code Patterns | Django + Next.js | v1.0

---

## Table of Contents

1. [Stack Overview](#stack-overview)
2. [Project Structure](#project-structure)
3. [Backend — Django Patterns](#backend--django-patterns)
4. [Frontend — Nextjs Patterns](#frontend--nextjs-patterns)
5. [API Design](#api-design)
6. [Database Patterns](#database-patterns)
7. [ETL Pipeline Patterns](#etl-pipeline-patterns)
8. [Security](#security)
9. [Testing Strategy](#testing-strategy)
10. [UI Component System](#ui-component-system)

---

## Stack Overview

```
Frontend          Backend            Data
Next.js 14+       Django 5.x         PostgreSQL 16
TypeScript        Django REST Fw.    Redis (cache)
Tailwind CSS      Celery (tasks)     Celery Beat
shadcn/ui         Python 3.12+       (scheduling)
Recharts          uv / pip
```

**Ly do chon:**
- **Django**: batteries-included, ORM manh, DRF chuan REST, Celery integration tot cho ETL async
- **Next.js App Router**: SSR/SSG linh hoat, toi uu SEO, file-based routing sach, React Server Components
- **PostgreSQL**: JSON support tot cho social data, window functions cho analytics
- **Redis**: cache API responses, Celery broker, rate-limit counters

---

## Project Structure

```
sociallens-bi/
├── backend/
│   ├── config/
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   └── celery.py
│   ├── apps/
│   │   ├── social_data/
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── tasks.py
│   │   │   └── services/
│   │   │       ├── facebook.py
│   │   │       ├── youtube.py
│   │   │       └── sentiment.py
│   │   ├── analytics/
│   │   │   ├── models.py
│   │   │   ├── views.py
│   │   │   └── queries.py
│   │   └── dashboard/
│   │       └── views.py
│   ├── common/
│   │   ├── exceptions.py
│   │   ├── pagination.py
│   │   └── models.py
│   └── manage.py
│
├── frontend/
│   ├── app/
│   │   ├── (dashboard)/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── sentiment/page.tsx
│   │   │   ├── content/page.tsx
│   │   │   └── competitors/page.tsx
│   │   └── globals.css
│   ├── components/
│   │   ├── ui/              # shadcn/ui base — khong sua
│   │   ├── charts/
│   │   │   ├── EngagementChart.tsx
│   │   │   ├── SentimentGauge.tsx
│   │   │   └── HeatmapChart.tsx
│   │   ├── dashboard/
│   │   │   ├── KPICard.tsx
│   │   │   └── DateRangePicker.tsx
│   │   └── layout/
│   │       ├── Sidebar.tsx
│   │       └── Header.tsx
│   ├── lib/
│   │   ├── api.ts
│   │   └── utils.ts
│   ├── hooks/
│   │   └── useAnalytics.ts
│   └── types/index.ts
│
├── docker-compose.yml
├── .env.example
└── Makefile
```

---

## Backend — Django Patterns

### 1. Settings Splitting (12-factor style)

```python
# config/settings/base.py
from pathlib import Path
import environ

env = environ.Env()
BASE_DIR = Path(__file__).resolve().parent.parent.parent

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "django_filters",
    "celery",
]

LOCAL_APPS = [
    "apps.social_data",
    "apps.analytics",
    "apps.dashboard",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "common.pagination.StandardResultsPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/day",
        "user": "1000/day",
    },
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "EXCEPTION_HANDLER": "common.exceptions.custom_exception_handler",
}
```

### 2. Abstract Base Models

```python
# common/models.py
import uuid
from django.db import models


class TimeStampedModel(models.Model):
    """Base model voi created_at, updated_at tu dong."""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDModel(TimeStampedModel):
    """Base model dung UUID primary key."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


# apps/social_data/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from common.models import UUIDModel


class Platform(models.TextChoices):
    FACEBOOK = "facebook", _("Facebook")
    YOUTUBE = "youtube", _("YouTube")
    TIKTOK = "tiktok", _("TikTok")
    INSTAGRAM = "instagram", _("Instagram")


class SocialPost(UUIDModel):
    platform = models.CharField(max_length=20, choices=Platform.choices, db_index=True)
    external_id = models.CharField(max_length=255, unique=True)
    page_name = models.CharField(max_length=255, db_index=True)
    reach = models.BigIntegerField(default=0)
    impressions = models.BigIntegerField(default=0)
    likes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    engagement_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    content_type = models.CharField(max_length=50)
    posted_at = models.DateTimeField(db_index=True)

    class Meta:
        db_table = "social_posts"
        ordering = ["-posted_at"]
        indexes = [
            models.Index(fields=["platform", "posted_at"]),
            models.Index(fields=["page_name", "platform"]),
        ]

    @property
    def computed_engagement_rate(self) -> float:
        """Tinh engagement rate an toan, tranh division by zero."""
        if not self.reach:
            return 0.0
        return round((self.likes + self.comments + self.shares) / self.reach * 100, 2)

    def save(self, *args, **kwargs):
        self.engagement_rate = self.computed_engagement_rate
        super().save(*args, **kwargs)


class SentimentLabel(models.TextChoices):
    POSITIVE = "positive", _("Tich cuc")
    NEUTRAL = "neutral", _("Trung tinh")
    NEGATIVE = "negative", _("Tieu cuc")


class Comment(UUIDModel):
    post = models.ForeignKey(SocialPost, on_delete=models.CASCADE, related_name="comments_set")
    external_id = models.CharField(max_length=255, unique=True)
    text = models.TextField()
    sentiment_label = models.CharField(
        max_length=20, choices=SentimentLabel.choices, null=True, db_index=True
    )
    sentiment_score = models.FloatField(null=True)  # -1.0 to +1.0
    commented_at = models.DateTimeField(db_index=True)

    class Meta:
        db_table = "comments"
        indexes = [
            models.Index(fields=["post", "sentiment_label"]),
            models.Index(fields=["commented_at"]),
        ]
```

### 3. Service Layer Pattern

Logic nam trong service layer — KHONG nam trong view hay model.

```python
# apps/social_data/services/facebook.py
import logging
from dataclasses import dataclass
from typing import Iterator
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class PostData:
    external_id: str
    page_name: str
    reach: int
    likes: int
    comments: int
    shares: int
    content_type: str
    posted_at: str


class FacebookAPIError(Exception):
    pass


class FacebookService:
    BASE_URL = "https://graph.facebook.com/v19.0"

    def __init__(self, access_token: str | None = None):
        self.access_token = access_token or settings.FACEBOOK_ACCESS_TOKEN
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})

    def _get(self, endpoint: str, params: dict) -> dict:
        """HTTP GET voi error handling nhat quan."""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/{endpoint}", params=params, timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            logger.error("Facebook API error: %s — %s", endpoint, e)
            raise FacebookAPIError(str(e)) from e
        except requests.Timeout:
            logger.error("Facebook API timeout: %s", endpoint)
            raise FacebookAPIError("Request timed out") from None

    def fetch_page_posts(self, page_id: str, since: str, until: str) -> Iterator[PostData]:
        """Generator de stream posts, tiet kiem bo nho khi data lon."""
        params = {
            "fields": "id,message,created_time,insights.metric(post_impressions)",
            "since": since,
            "until": until,
            "limit": 100,
        }
        while True:
            data = self._get(f"{page_id}/posts", params)
            for post in data.get("data", []):
                yield self._parse_post(post)
            if not data.get("paging", {}).get("next"):
                break
            params["after"] = data["paging"]["cursors"]["after"]

    @staticmethod
    def _parse_post(raw: dict) -> PostData:
        insights = {
            m["name"]: m["values"][0]["value"]
            for m in raw.get("insights", {}).get("data", [])
        }
        return PostData(
            external_id=raw["id"],
            page_name=raw.get("from", {}).get("name", ""),
            reach=insights.get("post_impressions", 0),
            likes=raw.get("reactions", {}).get("summary", {}).get("total_count", 0),
            comments=raw.get("comments", {}).get("summary", {}).get("total_count", 0),
            shares=raw.get("shares", {}).get("count", 0),
            content_type="image" if "full_picture" in raw else "text",
            posted_at=raw["created_time"],
        )
```

### 4. Celery Task Patterns

```python
# apps/social_data/tasks.py
from celery import shared_task
from celery.utils.log import get_task_logger
from django.db import transaction
from .services.facebook import FacebookService, FacebookAPIError
from .models import SocialPost, Platform

logger = get_task_logger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(FacebookAPIError,),
    acks_late=True,  # dam bao task khong mat khi worker crash
)
def sync_facebook_posts(self, page_id: str, since: str, until: str):
    """Dong bo bai dang Facebook vao DB."""
    logger.info("Syncing Facebook posts for page %s", page_id)
    service = FacebookService()
    posts_synced = 0

    try:
        with transaction.atomic():
            for post_data in service.fetch_page_posts(page_id, since, until):
                SocialPost.objects.update_or_create(
                    external_id=post_data.external_id,
                    defaults={
                        "platform": Platform.FACEBOOK,
                        "page_name": post_data.page_name,
                        "reach": post_data.reach,
                        "likes": post_data.likes,
                        "comments": post_data.comments,
                        "shares": post_data.shares,
                        "content_type": post_data.content_type,
                        "posted_at": post_data.posted_at,
                    },
                )
                posts_synced += 1

        logger.info("Synced %d posts for page %s", posts_synced, page_id)
        return {"posts_synced": posts_synced}

    except Exception as exc:
        logger.exception("Failed to sync posts for page %s", page_id)
        raise self.retry(exc=exc)


# config/celery_beat_schedule.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "sync-facebook-daily": {
        "task": "apps.social_data.tasks.sync_facebook_posts",
        "schedule": crontab(hour=2, minute=0),
        "kwargs": {"page_id": "your_page_id", "since": "7daysAgo", "until": "today"},
    },
    "compute-kpis-hourly": {
        "task": "apps.analytics.tasks.compute_kpis",
        "schedule": crontab(minute=0),
    },
}
```

### 5. ViewSet + Analytics Queries

```python
# apps/analytics/views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .queries import get_engagement_summary, get_posting_heatmap


class AnalyticsViewSet(viewsets.ViewSet):
    """
    GET /api/v1/analytics/engagement/
    GET /api/v1/analytics/sentiment/
    GET /api/v1/analytics/heatmap/
    GET /api/v1/analytics/competitors/
    """

    @action(detail=False, methods=["get"])
    @method_decorator(cache_page(60 * 15))  # cache 15 phut
    def engagement(self, request):
        data = get_engagement_summary(
            platform=request.query_params.get("platform"),
            start_date=request.query_params.get("start_date"),
            end_date=request.query_params.get("end_date"),
        )
        return Response(data)

    @action(detail=False, methods=["get"])
    @method_decorator(cache_page(60 * 60))  # cache 1 gio
    def heatmap(self, request):
        return Response(get_posting_heatmap())


# apps/analytics/queries.py
from django.db import connection
from django.db.models import Avg, Count, Sum, F
from apps.social_data.models import SocialPost


def get_engagement_summary(platform=None, start_date=None, end_date=None):
    """ORM query cho summary data."""
    qs = SocialPost.objects.all()
    if platform:
        qs = qs.filter(platform=platform)
    if start_date:
        qs = qs.filter(posted_at__date__gte=start_date)
    if end_date:
        qs = qs.filter(posted_at__date__lte=end_date)

    return (
        qs.values("platform", date=F("posted_at__date"))
        .annotate(
            avg_engagement_rate=Avg("engagement_rate"),
            total_reach=Sum("reach"),
            total_posts=Count("id"),
        )
        .order_by("date")
    )


def get_posting_heatmap():
    """Raw SQL cho window function phuc tap."""
    sql = """
        SELECT
            EXTRACT(DOW FROM posted_at AT TIME ZONE 'Asia/Ho_Chi_Minh') AS day_of_week,
            EXTRACT(HOUR FROM posted_at AT TIME ZONE 'Asia/Ho_Chi_Minh') AS hour_of_day,
            COUNT(*) AS post_count,
            ROUND(AVG(engagement_rate)::numeric, 2) AS avg_engagement
        FROM social_posts
        WHERE posted_at >= NOW() - INTERVAL '90 days'
        GROUP BY 1, 2
        ORDER BY avg_engagement DESC
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
```

---

## Frontend — Next.js Patterns

### 1. Next.js Config

```typescript
// next.config.ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    typedRoutes: true,
  },
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: `${process.env.DJANGO_API_URL}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;
```

### 2. API Client (type-safe)

```typescript
// lib/api.ts
// Single client, tai su dung toan app

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "/api/v1";

export class APIError extends Error {
  constructor(
    public status: number,
    message: string,
    public data?: unknown
  ) {
    super(message);
    this.name = "APIError";
  }
}

async function request<T>(endpoint: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: { "Content-Type": "application/json", ...init.headers },
    ...init,
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new APIError(res.status, `API error ${res.status}`, data);
  }
  return res.json() as Promise<T>;
}

export const api = {
  analytics: {
    engagement: (params: Record<string, string>) =>
      request<EngagementSummary[]>(
        `/analytics/engagement/?${new URLSearchParams(params)}`
      ),
    sentiment: (params: Record<string, string>) =>
      request<SentimentTrend[]>(
        `/analytics/sentiment/?${new URLSearchParams(params)}`
      ),
    heatmap: () => request<HeatmapData[]>("/analytics/heatmap/"),
    competitors: () => request<CompetitorData[]>("/analytics/competitors/"),
  },
};
```

### 3. Server Component Pattern (App Router)

```typescript
// app/(dashboard)/page.tsx
// React Server Component — fetch data truc tiep, khong useEffect

import { Suspense } from "react";
import { KPICard, KPICardSkeleton } from "@/components/dashboard/KPICard";
import { EngagementChart } from "@/components/charts/EngagementChart";
import { api } from "@/lib/api";

export const revalidate = 900; // ISR: revalidate moi 15 phut

export default async function DashboardPage() {
  // Parallel fetch de giam latency
  const [engagement, heatmap] = await Promise.all([
    api.analytics.engagement({ days: "30" }),
    api.analytics.heatmap(),
  ]);

  return (
    <main className="space-y-6 p-6">
      <section className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <Suspense fallback={<KPICardSkeleton />}>
          <KPISummaryCards data={engagement} />
        </Suspense>
      </section>
      <EngagementChart data={engagement} />
    </main>
  );
}
```

### 4. KPICard Component

```typescript
// components/dashboard/KPICard.tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { TrendingUp, TrendingDown } from "lucide-react";
import { cn } from "@/lib/utils";

interface KPICardProps {
  title: string;
  value: string | number;
  change?: number;
  description?: string;
}

export function KPICard({ title, value, change, description }: KPICardProps) {
  const isPositive = (change ?? 0) >= 0;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        {change !== undefined && (
          <span
            className={cn(
              "flex items-center gap-1 text-xs font-medium",
              isPositive ? "text-emerald-600" : "text-red-500"
            )}
          >
            {isPositive ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
            {Math.abs(change).toFixed(1)}%
          </span>
        )}
      </CardHeader>
      <CardContent>
        <p className="text-2xl font-semibold tracking-tight">{value}</p>
        {description && (
          <p className="mt-1 text-xs text-muted-foreground">{description}</p>
        )}
      </CardContent>
    </Card>
  );
}

export function KPICardSkeleton() {
  return (
    <Card>
      <CardHeader className="pb-2">
        <Skeleton className="h-4 w-24" />
      </CardHeader>
      <CardContent>
        <Skeleton className="h-8 w-16" />
      </CardContent>
    </Card>
  );
}
```

### 5. Engagement Chart (Recharts)

```typescript
// components/charts/EngagementChart.tsx
"use client";

import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Props {
  data: EngagementSummary[];
}

const PLATFORM_COLORS: Record<string, string> = {
  facebook: "#1877F2",
  youtube: "#FF0000",
  tiktok: "#010101",
  instagram: "#E1306C",
};

export function EngagementChart({ data }: Props) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base font-medium">
          Engagement Rate theo thoi gian
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={320}>
          <LineChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }}
            />
            <YAxis
              tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }}
              tickFormatter={(v) => `${v}%`}
            />
            <Tooltip
              formatter={(v: number) => [`${v.toFixed(2)}%`, "Engagement"]}
              contentStyle={{
                background: "hsl(var(--background))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "var(--radius)",
              }}
            />
            <Legend />
            {Object.entries(PLATFORM_COLORS).map(([platform, color]) => (
              <Line
                key={platform}
                type="monotone"
                dataKey={platform}
                stroke={color}
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
```

### 6. Tailwind Config (Design Tokens)

```typescript
// tailwind.config.ts
import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        platform: {
          facebook: "#1877F2",
          youtube: "#FF0000",
          tiktok: "#010101",
          instagram: "#E1306C",
        },
        sentiment: {
          positive: "#10B981",
          neutral: "#6B7280",
          negative: "#EF4444",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      fontFamily: {
        sans: ["var(--font-geist-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-geist-mono)", "monospace"],
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
```

---

## API Design

### RESTful Endpoint Conventions

```
GET  /api/v1/posts/                    — Danh sach posts (paginated)
GET  /api/v1/posts/{id}/               — Chi tiet post
GET  /api/v1/analytics/engagement/     — Engagement summary
GET  /api/v1/analytics/sentiment/      — Sentiment trend
GET  /api/v1/analytics/heatmap/        — Posting heatmap
GET  /api/v1/analytics/competitors/    — Competitor comparison
POST /api/v1/sync/facebook/            — Trigger sync thu cong
GET  /api/v1/sync/status/              — Trang thai sync

Query params chuan:
  ?platform=facebook&start_date=2024-01-01&end_date=2024-01-31
  ?page=1&page_size=20
  ?ordering=-engagement_rate
```

### Response Format

```json
// Thanh cong — danh sach
{
  "count": 142,
  "next": "https://api/v1/posts/?page=2",
  "previous": null,
  "results": []
}

// Loi — chuan hoa theo DRF
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Du lieu khong hop le",
    "details": {
      "start_date": ["Ngay bat dau khong duoc lon hon ngay ket thuc"]
    }
  }
}
```

---

## Database Patterns

### Index Migration Pattern

```python
# apps/social_data/migrations/0002_add_analytics_indexes.py
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("social_data", "0001_initial")]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE INDEX CONCURRENTLY IF NOT EXISTS
                idx_posts_platform_date
                ON social_posts (platform, DATE(posted_at));

                CREATE INDEX CONCURRENTLY IF NOT EXISTS
                idx_comments_sentiment_date
                ON comments (sentiment_label, commented_at);
            """,
            reverse_sql="""
                DROP INDEX IF EXISTS idx_posts_platform_date;
                DROP INDEX IF EXISTS idx_comments_sentiment_date;
            """,
        )
    ]
```

### PostgreSQL Analytics Query

```sql
-- Ranking bai dang theo engagement trong tung platform
SELECT
    platform,
    external_id,
    engagement_rate,
    RANK() OVER (
        PARTITION BY platform
        ORDER BY engagement_rate DESC
    ) AS rank_in_platform,
    ROUND(AVG(engagement_rate) OVER (PARTITION BY platform), 2) AS platform_avg,
    engagement_rate - AVG(engagement_rate) OVER (PARTITION BY platform) AS delta_from_avg
FROM social_posts
WHERE posted_at >= NOW() - INTERVAL '30 days'
ORDER BY platform, rank_in_platform;
```

---

## ETL Pipeline Patterns

```python
# Base ETL class — Extract, Transform, Load voi error isolation

import logging
from abc import ABC, abstractmethod


class ETLPipeline(ABC):
    def __init__(self, source: str):
        self.source = source
        self.logger = logging.getLogger(f"etl.{source}")
        self.stats = {"extracted": 0, "transformed": 0, "loaded": 0, "errors": 0}

    def run(self, **kwargs) -> dict:
        self.logger.info("Starting ETL for %s", self.source)
        try:
            raw = self.extract(**kwargs)
            self.stats["extracted"] = len(raw)

            clean = self.transform(raw)
            self.stats["transformed"] = len(clean)

            self.load(clean)
            self.stats["loaded"] = len(clean)

        except Exception:
            self.logger.exception("ETL failed for %s", self.source)
            self.stats["errors"] += 1
            raise
        finally:
            self.logger.info("ETL stats: %s", self.stats)

        return self.stats

    @abstractmethod
    def extract(self, **kwargs): ...

    @abstractmethod
    def transform(self, data): ...

    @abstractmethod
    def load(self, data): ...
```

---

## Security

```python
# common/permissions.py
from rest_framework.permissions import BasePermission


class IsAnalystOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.groups.filter(name__in=["analyst", "admin"]).exists()
        )


# config/settings/base.py
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOW_CREDENTIALS = True

# API keys luu trong env, khong hardcode
FACEBOOK_ACCESS_TOKEN = env("FACEBOOK_ACCESS_TOKEN")
YOUTUBE_API_KEY = env("YOUTUBE_API_KEY")
```

---

## Testing Strategy

```python
# pytest + pytest-django
# apps/social_data/tests/test_services.py

import pytest
from unittest.mock import patch, MagicMock
from apps.social_data.services.facebook import FacebookService, FacebookAPIError


@pytest.fixture
def service():
    return FacebookService(access_token="test_token")


@patch("apps.social_data.services.facebook.requests.Session")
def test_fetch_posts_success(mock_session, service):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "data": [{"id": "123", "created_time": "2024-01-01T10:00:00+0000"}],
        "paging": {},
    }
    mock_session.return_value.get.return_value = mock_resp

    posts = list(service.fetch_page_posts("page_id", "2024-01-01", "2024-01-31"))
    assert len(posts) == 1


@patch("apps.social_data.services.facebook.requests.Session")
def test_fetch_posts_raises_on_http_error(mock_session, service):
    mock_session.return_value.get.return_value.raise_for_status.side_effect = (
        Exception("403 Forbidden")
    )
    with pytest.raises(FacebookAPIError):
        list(service.fetch_page_posts("page_id", "2024-01-01", "2024-01-31"))
```

```typescript
// frontend/__tests__/KPICard.test.tsx
import { render, screen } from "@testing-library/react";
import { KPICard } from "@/components/dashboard/KPICard";

describe("KPICard", () => {
  it("renders value and title", () => {
    render(<KPICard title="Engagement Rate" value="3.45%" change={2.1} />);
    expect(screen.getByText("Engagement Rate")).toBeInTheDocument();
    expect(screen.getByText("3.45%")).toBeInTheDocument();
  });

  it("shows negative trend in red for negative change", () => {
    render(<KPICard title="Reach" value="10K" change={-5.2} />);
    const trend = screen.getByText("5.2%");
    expect(trend.closest("span")).toHaveClass("text-red-500");
  });
});
```

---

## UI Component System

### CSS Variables (globals.css)

```css
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222 47% 11%;
    --muted: 210 40% 96%;
    --muted-foreground: 215 16% 47%;
    --border: 214 32% 91%;
    --primary: 221 83% 53%;
    --primary-foreground: 0 0% 100%;
    --radius: 0.5rem;

    /* Chart colors — accessible WCAG AA */
    --chart-facebook: 214 89% 52%;
    --chart-youtube: 0 100% 50%;
    --chart-positive: 160 84% 39%;
    --chart-negative: 0 84% 60%;
    --chart-neutral: 220 9% 46%;
  }

  .dark {
    --background: 222 47% 11%;
    --foreground: 210 40% 98%;
    --muted: 217 33% 17%;
    --border: 217 33% 17%;
    --primary: 213 94% 68%;
  }
}
```

### Component Conventions

```
Naming:        PascalCase cho components (KPICard, EngagementChart)
Location:      components/ui/        <- shadcn base, khong sua truc tiep
               components/charts/    <- chart wrappers
               components/dashboard/ <- domain-specific components
Props:         Interface truoc component, suffix Props
Exports:       Named exports (tru page.tsx cua Next.js dung default)
Client/Server: "use client" chi khi can hooks hoac event handlers
               Server Component la default -> tot cho performance
Data:          Server Components fetch data truc tiep
               Client Components nhan data qua props
               Toi thieu hoa useEffect, uu tien Server Actions
```

---

*SocialLens BI | DESIGN.md v1.0 | Django 5.x + Next.js 14+ | 2024*
