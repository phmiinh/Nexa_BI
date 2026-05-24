export type Tone = "positive" | "warning" | "neutral";

export type Kpi = {
  label: string;
  value: string;
  delta: string;
  tone: Tone;
};

export type Overview = {
  dateRange: string;
  kpis: Kpi[];
  finding: {
    title: string;
    body: string;
    action: string;
  };
};

export type SourceConfidence = {
  level: "high" | "medium" | "low";
  score: number;
  detail: string;
};

export type DataFreshness = {
  dataFrom?: string;
  dataThrough: string;
  generatedAt: string;
  ageHours?: number;
  status: "fresh" | "stale" | "unknown";
};

export type InsightItem = {
  title: string;
  detail: string;
  metric?: string;
  tone: Tone;
};

export type BIInsights = {
  generatedAt: string;
  source: string;
  sourceConfidence: SourceConfidence;
  freshness: DataFreshness;
  highlights: InsightItem[];
  risks: InsightItem[];
  recommendations: string[];
};

export type EngagementPoint = {
  date: string;
  engagementRate: number;
  reach: number;
};

export type SentimentPoint = {
  date: string;
  positive: number;
  neutral: number;
  negative: number;
};

export type ContentPerformance = {
  contentType: string;
  posts: number;
  reach: number;
  engagementRate: number;
  viralityScore: number;
};

export type Competitor = {
  brand: string;
  posts: number;
  shareOfVoice: number;
  engagementRate: number;
  sentimentRatio: number;
};

export type Post = {
  id: string;
  platform: string;
  brand: string;
  contentType: string;
  message: string;
  createdAt: string;
  reach: number;
  engagementCount: number;
  engagementRate: number;
  viralityScore: number;
  sentimentRatio: number;
};

export type HeatmapCell = {
  day: string;
  hour: string;
  engagementRate: number;
};

export type SyncStatus = {
  status: string;
  lastRunAt: string;
  source: string;
  processedPosts: number;
  processedComments: number;
  qualityPassed: boolean;
  freshness: DataFreshness;
  sourceConfidence: SourceConfidence;
  checks: Array<{
    name: string;
    status: "passed" | "warning" | "failed";
    detail: string;
  }>;
};
