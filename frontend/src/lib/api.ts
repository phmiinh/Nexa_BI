import competitorsFallback from "@/data/competitors.json";
import contentFallback from "@/data/content-performance.json";
import engagementFallback from "@/data/engagement.json";
import heatmapFallback from "@/data/heatmap.json";
import overviewFallback from "@/data/overview.json";
import postsFallback from "@/data/posts.json";
import sentimentFallback from "@/data/sentiment.json";
import syncStatusFallback from "@/data/sync-status.json";
import type {
  Competitor,
  ContentPerformance,
  EngagementPoint,
  HeatmapCell,
  Overview,
  Post,
  SentimentPoint,
  SyncStatus
} from "@/lib/types";

async function fetchApi<T>(endpoint: string, fallback: T, transform?: (payload: unknown) => T): Promise<T> {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;

  if (!apiBaseUrl) {
    return fallback;
  }

  try {
    const response = await fetch(`${apiBaseUrl}${endpoint}`, {
      cache: "no-store",
      headers: {
        accept: "application/json"
      }
    });

    if (!response.ok) {
      return fallback;
    }

    const payload = await response.json();
    return transform ? transform(payload) : (payload as T);
  } catch {
    return fallback;
  }
}

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" ? (value as Record<string, unknown>) : {};
}

function asArray(value: unknown): Record<string, unknown>[] {
  return Array.isArray(value) ? value.map(asRecord) : [];
}

function resultArray(payload: unknown): Record<string, unknown>[] {
  const record = asRecord(payload);
  return Array.isArray(record.results) ? asArray(record.results) : asArray(payload);
}

function numberValue(value: unknown): number {
  const parsed = Number(value ?? 0);
  return Number.isFinite(parsed) ? parsed : 0;
}

function stringValue(value: unknown): string {
  return String(value ?? "");
}

function percentText(value: unknown): string {
  return `${numberValue(value).toFixed(1)}%`;
}

function compactText(value: unknown): string {
  return Intl.NumberFormat("en", { notation: "compact", maximumFractionDigits: 1 }).format(
    numberValue(value)
  );
}

function normalizeOverview(payload: unknown): Overview {
  const record = asRecord(payload);
  if (Array.isArray(record.kpis)) {
    return record as Overview;
  }
  const dateFrom = stringValue(record.date_from);
  const dateTo = stringValue(record.date_to);
  return {
    dateRange: dateFrom && dateTo ? `${dateFrom} to ${dateTo}` : "Processed dataset",
    kpis: [
      {
        label: "Total engagement",
        value: compactText(record.total_engagement),
        delta: "SQL validated",
        tone: "positive"
      },
      {
        label: "Engagement rate",
        value: percentText(record.avg_engagement_rate),
        delta: "avg",
        tone: "positive"
      },
      {
        label: "Virality score",
        value: percentText(record.avg_virality_score),
        delta: "avg",
        tone: "neutral"
      },
      {
        label: "Total reach",
        value: compactText(record.total_reach),
        delta: "warehouse",
        tone: "positive"
      }
    ],
    finding: {
      title: "Warehouse metrics are available",
      body: "Dashboard values are loaded from SocialLens BI processed data or PostgreSQL views.",
      action: "Use Power BI and SQL validation queries to confirm the final submission metrics."
    }
  };
}

function normalizeEngagement(payload: unknown): EngagementPoint[] {
  return resultArray(payload).map((item) => ({
    date: stringValue(item.full_date ?? item.date),
    engagementRate: numberValue(item.avg_engagement_rate ?? item.engagementRate),
    reach: numberValue(item.total_reach ?? item.reach)
  }));
}

function normalizeSentiment(payload: unknown): SentimentPoint[] {
  return resultArray(payload).map((item) => ({
    date: stringValue(item.full_date ?? item.date),
    positive: numberValue(item.positive_count ?? item.positive),
    neutral: numberValue(item.neutral_count ?? item.neutral),
    negative: numberValue(item.negative_count ?? item.negative)
  }));
}

function normalizeContent(payload: unknown): ContentPerformance[] {
  return resultArray(payload).map((item) => ({
    contentType: stringValue(item.content_type ?? item.contentType),
    posts: numberValue(item.post_count ?? item.posts),
    reach: numberValue(item.total_reach ?? item.reach),
    engagementRate: numberValue(item.avg_engagement_rate ?? item.engagementRate),
    viralityScore: numberValue(item.avg_virality_score ?? item.viralityScore)
  }));
}

function normalizeCompetitors(payload: unknown): Competitor[] {
  return resultArray(payload).map((item) => ({
    brand: stringValue(item.page_name ?? item.brand),
    posts: numberValue(item.post_count ?? item.posts),
    shareOfVoice: numberValue(item.share_of_voice ?? item.shareOfVoice),
    engagementRate: numberValue(item.avg_engagement_rate ?? item.engagementRate),
    sentimentRatio: numberValue(item.sentiment_ratio ?? item.sentimentRatio)
  }));
}

function normalizePosts(payload: unknown): Post[] {
  return resultArray(payload).map((item) => ({
    id: stringValue(item.post_id ?? item.external_post_id ?? item.id),
    platform: stringValue(item.platform_name ?? item.platform),
    brand: stringValue(item.page_name ?? item.brand),
    contentType: stringValue(item.content_type ?? item.contentType),
    message: stringValue(item.caption ?? item.content_text ?? item.message),
    createdAt: stringValue(item.full_timestamp ?? item.createdAt ?? item.date),
    reach: numberValue(item.reach),
    engagementCount: numberValue(item.engagement_count ?? item.engagementCount),
    engagementRate: numberValue(item.engagement_rate ?? item.engagementRate),
    viralityScore: numberValue(item.virality_score ?? item.viralityScore),
    sentimentRatio: numberValue(item.sentiment_ratio ?? item.sentimentRatio)
  }));
}

function normalizeHeatmap(payload: unknown): HeatmapCell[] {
  return resultArray(payload).map((item) => ({
    day: stringValue(item.day_name ?? item.day),
    hour: stringValue(item.hour_of_day ?? item.hour),
    engagementRate: numberValue(item.avg_engagement_rate ?? item.engagementRate)
  }));
}

function normalizeSyncStatus(payload: unknown): SyncStatus {
  const record = asRecord(payload);
  if (Array.isArray(record.checks)) {
    return record as SyncStatus;
  }
  return {
    status: stringValue(record.status || "available"),
    lastRunAt: stringValue(record.finished_at ?? record.posts_modified_at ?? "n/a"),
    source: stringValue(record.source ?? record.source_type ?? "processed_csv"),
    processedPosts: numberValue(record.loaded_posts),
    processedComments: numberValue(record.loaded_comments),
    qualityPassed: record.status !== "missing",
    checks: [
      {
        name: "Data source",
        status: record.status === "missing" ? "warning" : "passed",
        detail: stringValue(record.source ?? record.posts_path ?? "processed data")
      }
    ]
  };
}

export function getOverview(): Promise<Overview> {
  return fetchApi("/api/v1/analytics/overview/", overviewFallback as Overview, normalizeOverview);
}

export function getEngagement(): Promise<EngagementPoint[]> {
  return fetchApi(
    "/api/v1/analytics/engagement/",
    engagementFallback as EngagementPoint[],
    normalizeEngagement
  );
}

export function getSentiment(): Promise<SentimentPoint[]> {
  return fetchApi(
    "/api/v1/analytics/sentiment/",
    sentimentFallback as SentimentPoint[],
    normalizeSentiment
  );
}

export function getContentPerformance(): Promise<ContentPerformance[]> {
  return fetchApi(
    "/api/v1/analytics/content-performance/",
    contentFallback as ContentPerformance[],
    normalizeContent
  );
}

export function getCompetitors(): Promise<Competitor[]> {
  return fetchApi(
    "/api/v1/analytics/competitors/",
    competitorsFallback as Competitor[],
    normalizeCompetitors
  );
}

export function getPosts(): Promise<Post[]> {
  return fetchApi("/api/v1/posts/", postsFallback as Post[], normalizePosts);
}

export function getTopPosts(): Promise<Post[]> {
  return fetchApi("/api/v1/analytics/top-posts/", postsFallback as Post[], normalizePosts);
}

export function getHeatmap(): Promise<HeatmapCell[]> {
  return fetchApi("/api/v1/analytics/heatmap/", heatmapFallback as HeatmapCell[], normalizeHeatmap);
}

export function getSyncStatus(): Promise<SyncStatus> {
  return fetchApi("/api/v1/sync/status/", syncStatusFallback as SyncStatus, normalizeSyncStatus);
}
