import competitorsFallback from "@/data/competitors.json";
import contentFallback from "@/data/content-performance.json";
import engagementFallback from "@/data/engagement.json";
import heatmapFallback from "@/data/heatmap.json";
import insightsFallback from "@/data/insights.json";
import overviewFallback from "@/data/overview.json";
import postsFallback from "@/data/posts.json";
import sentimentFallback from "@/data/sentiment.json";
import syncStatusFallback from "@/data/sync-status.json";
import type {
  BIInsights,
  Competitor,
  ContentPerformance,
  DataFreshness,
  EngagementPoint,
  HeatmapCell,
  InsightItem,
  Overview,
  Post,
  SentimentPoint,
  SourceConfidence,
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

function sourceConfidenceValue(value: unknown, fallbackSource: string): SourceConfidence {
  const record = asRecord(value);
  const level = stringValue(record.level || "medium");
  return {
    level: level === "high" || level === "low" ? level : "medium",
    score: numberValue(record.score || 0.7),
    detail: stringValue(record.detail || record.reason || `Loaded from ${fallbackSource}`)
  };
}

function freshnessValue(value: unknown, generatedAt: string): DataFreshness {
  const record = asRecord(value);
  const status = stringValue(record.status || "unknown");
  return {
    dataFrom: record.dataFrom ? stringValue(record.dataFrom) : undefined,
    dataThrough: stringValue(record.dataThrough || record.data_through || generatedAt),
    generatedAt: stringValue(record.generatedAt || record.generated_at || generatedAt),
    ageHours: record.ageHours || record.age_hours ? numberValue(record.ageHours || record.age_hours) : undefined,
    status: status === "fresh" || status === "stale" ? status : "unknown"
  };
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
    const syncStatus = record as SyncStatus;
    return {
      ...syncStatus,
      freshness: syncStatus.freshness || freshnessValue(record.freshness, syncStatus.lastRunAt),
      sourceConfidence:
        syncStatus.sourceConfidence || sourceConfidenceValue(record.sourceConfidence, syncStatus.source)
    };
  }
  const lastRunAt = stringValue(record.finished_at ?? record.posts_modified_at ?? "n/a");
  const source = stringValue(record.source ?? record.source_type ?? "processed_csv");
  const counts = asRecord(record.counts);
  return {
    status: stringValue(record.status || "available"),
    lastRunAt,
    source,
    processedPosts: numberValue(counts.posts ?? record.loaded_posts),
    processedComments: numberValue(counts.comments ?? record.loaded_comments),
    qualityPassed: record.status !== "missing",
    freshness: freshnessValue(record.freshness, lastRunAt),
    sourceConfidence: sourceConfidenceValue(record.sourceConfidence || record.source_confidence, source),
    checks: [
      {
        name: "Data source",
        status: record.status === "missing" ? "warning" : "passed",
        detail: stringValue(record.source ?? record.posts_path ?? "processed data")
      }
    ]
  };
}

function normalizeInsightItems(value: unknown): InsightItem[] {
  return asArray(value).map((item) => ({
    title: stringValue(item.title),
    detail: stringValue(item.detail),
    metric: item.metric ? stringValue(item.metric) : undefined,
    tone:
      item.tone === "positive" || item.tone === "warning" || item.tone === "neutral"
        ? item.tone
        : "neutral"
  }));
}

function normalizeInsights(payload: unknown): BIInsights {
  const record = asRecord(asRecord(payload).result || payload);
  const generatedAt = stringValue(record.generatedAt || record.generated_at || new Date().toISOString());
  const source = stringValue(record.source || "api");
  const apiInsights = asArray(record.insights);
  const apiHighlights = apiInsights.map((item) => ({
    title: stringValue(item.title),
    detail: stringValue(item.message || item.detail),
    metric: item.type ? stringValue(item.type) : undefined,
    tone: "neutral" as const
  }));
  return {
    generatedAt,
    source,
    sourceConfidence: sourceConfidenceValue(record.sourceConfidence || record.source_confidence, source),
    freshness: freshnessValue(record.freshness, generatedAt),
    highlights: apiHighlights.length ? apiHighlights : normalizeInsightItems(record.highlights),
    risks: normalizeInsightItems(record.risks),
    recommendations: Array.isArray(record.recommendations)
      ? record.recommendations.map((recommendation) => stringValue(recommendation))
      : []
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

export function getInsights(): Promise<BIInsights> {
  return fetchApi("/api/v1/analytics/insights/", insightsFallback as BIInsights, normalizeInsights);
}
