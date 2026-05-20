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
  checks: Array<{
    name: string;
    status: "passed" | "warning" | "failed";
    detail: string;
  }>;
};
