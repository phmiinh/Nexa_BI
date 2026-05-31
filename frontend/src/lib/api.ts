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
import { getDictionary, type Locale } from "@/lib/i18n";

async function fetchApi<T>(endpoint: string, transform?: (payload: unknown) => T): Promise<T> {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
  const isStatusEndpoint = endpoint.startsWith("/api/v1/sync/status/");

  const response = await fetch(`${apiBaseUrl}${endpoint}`, {
    ...(isStatusEndpoint ? { cache: "no-store" as const } : { next: { revalidate: 900 } }),
    headers: {
      accept: "application/json"
    }
  });

  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;
    try {
      const payload = await response.json();
      detail = String(asRecord(payload).detail || detail);
    } catch {
      // Keep the HTTP status text when the API error body is not JSON.
    }
    throw new Error(`SocialLens API request failed for ${endpoint}: ${detail}`);
  }

  const payload = await response.json();
  return transform ? transform(payload) : (payload as T);
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

function sourceConfidenceValue(value: unknown, sourceName: string): SourceConfidence {
  const record = asRecord(value);
  const level = stringValue(record.level || "medium");
  return {
    level: level === "high" || level === "low" ? level : "medium",
    score: numberValue(record.score || 0.7),
    detail: stringValue(record.detail || record.reason || `Loaded from ${sourceName}`)
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

function compactText(value: unknown, locale: Locale): string {
  return Intl.NumberFormat(locale === "vi" ? "vi-VN" : "en", { notation: "compact", maximumFractionDigits: 1 }).format(
    numberValue(value)
  );
}

function normalizeOverview(payload: unknown, locale: Locale): Overview {
  const dictionary = getDictionary(locale);
  const record = asRecord(payload);
  const dateFrom = stringValue(record.date_from);
  const dateTo = stringValue(record.date_to);
  return {
    dateRange: dateFrom && dateTo ? `${dateFrom} to ${dateTo}` : dictionary.overview.dateRangeFallback,
    kpis: [
      {
        label: dictionary.overview.kpis.totalEngagement,
        value: compactText(record.total_engagement, locale),
        delta: dictionary.common.sqlValidated,
        tone: "positive"
      },
      {
        label: dictionary.overview.kpis.engagementRate,
        value: percentText(record.avg_engagement_rate),
        delta: dictionary.common.average,
        tone: "positive"
      },
      {
        label: dictionary.overview.kpis.viralityScore,
        value: percentText(record.avg_virality_score),
        delta: dictionary.common.average,
        tone: "neutral"
      },
      {
        label: dictionary.overview.kpis.totalReach,
        value: compactText(record.total_reach, locale),
        delta: dictionary.common.warehouse,
        tone: "positive"
      }
    ],
    finding: dictionary.overview.finding
  };
}

function normalizeEngagement(payload: unknown): EngagementPoint[] {
  return sortByDate(
    resultArray(payload).map((item) => ({
      date: stringValue(item.full_date ?? item.date),
      engagementRate: numberValue(item.avg_engagement_rate ?? item.engagementRate),
      reach: numberValue(item.total_reach ?? item.reach)
    }))
  );
}

function normalizeSentiment(payload: unknown): SentimentPoint[] {
  return sortByDate(
    resultArray(payload).map((item) => {
      const positiveCount = numberValue(item.positive_count ?? item.positive);
      const neutralCount = numberValue(item.neutral_count ?? item.neutral);
      const negativeCount = numberValue(item.negative_count ?? item.negative);
      const total = positiveCount + neutralCount + negativeCount;
      return {
        date: stringValue(item.full_date ?? item.date),
        positive: item.positive_pct === undefined ? ratioPct(positiveCount, total) : numberValue(item.positive_pct),
        neutral: item.neutral_pct === undefined ? ratioPct(neutralCount, total) : numberValue(item.neutral_pct),
        negative: item.negative_pct === undefined ? ratioPct(negativeCount, total) : numberValue(item.negative_pct)
      };
    })
  );
}

function ratioPct(value: number, total: number): number {
  return total > 0 ? Number(((value / total) * 100).toFixed(1)) : 0;
}

function sortByDate<T extends { date: string }>(items: T[]): T[] {
  return [...items].sort((a, b) => Date.parse(a.date) - Date.parse(b.date));
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

function normalizeHeatmap(payload: unknown, locale: Locale): HeatmapCell[] {
  const days = getDictionary(locale).common.days;
  return resultArray(payload).map((item) => ({
    day: days[stringValue(item.day_name ?? item.day) as keyof typeof days] || stringValue(item.day_name ?? item.day),
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
      sourceConfidence: syncStatus.sourceConfidence || sourceConfidenceValue(record.sourceConfidence, syncStatus.source)
    };
  }
  const lastRunAt = stringValue(record.finished_at ?? record.posts_modified_at ?? "n/a");
  const sourceType = stringValue(record.source_type);
  const source = sourceType || stringValue(record.source ?? "warehouse");
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

function normalizeInsights(payload: unknown, locale: Locale): BIInsights {
  const dictionary = getDictionary(locale);
  const record = asRecord(asRecord(payload).result || payload);
  const generatedAt = stringValue(record.generatedAt || record.generated_at || new Date().toISOString());
  const source = stringValue(record.source || "warehouse");
  const apiInsights = asArray(record.insights);
  const apiHighlights = apiInsights.map((item) => ({
    title:
      dictionary.dashboard.insightTitles[
        stringValue(item.type) as keyof typeof dictionary.dashboard.insightTitles
      ] || stringValue(item.title),
    detail:
      dictionary.dashboard.insightDetails[
        stringValue(item.type) as keyof typeof dictionary.dashboard.insightDetails
      ] || stringValue(item.message || item.detail),
    metric: undefined,
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

export function getOverview(locale: Locale): Promise<Overview> {
  return fetchApi("/api/v1/analytics/overview/", (payload) =>
    normalizeOverview(payload, locale)
  );
}

export function getEngagement(limit = 120): Promise<EngagementPoint[]> {
  return fetchApi(
    `/api/v1/analytics/engagement/?limit=${limit}`,
    normalizeEngagement
  );
}

export function getSentiment(limit = 120): Promise<SentimentPoint[]> {
  return fetchApi(
    `/api/v1/analytics/sentiment/?limit=${limit}`,
    normalizeSentiment
  );
}

export function getContentPerformance(): Promise<ContentPerformance[]> {
  return fetchApi(
    "/api/v1/analytics/content-performance/",
    normalizeContent
  );
}

export function getCompetitors(): Promise<Competitor[]> {
  return fetchApi(
    "/api/v1/analytics/competitors/",
    normalizeCompetitors
  );
}

export function getPosts(limit = 100): Promise<Post[]> {
  return fetchApi(`/api/v1/posts/?limit=${limit}`, normalizePosts);
}

export function getTopPosts(): Promise<Post[]> {
  return fetchApi("/api/v1/analytics/top-posts/", normalizePosts);
}

export function getHeatmap(locale: Locale): Promise<HeatmapCell[]> {
  return fetchApi("/api/v1/analytics/heatmap/", (payload) =>
    normalizeHeatmap(payload, locale)
  );
}

export function getSyncStatus(): Promise<SyncStatus> {
  return fetchApi("/api/v1/sync/status/", normalizeSyncStatus);
}

export function getInsights(locale: Locale): Promise<BIInsights> {
  return fetchApi("/api/v1/analytics/insights/", (payload) =>
    normalizeInsights(payload, locale)
  );
}
