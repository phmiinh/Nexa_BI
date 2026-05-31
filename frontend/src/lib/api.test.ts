import { getCompetitors, getEngagement, getSyncStatus } from "@/lib/api";

function mockFetch(payload: unknown, ok = true) {
  const response = {
    ok,
    status: ok ? 200 : 503,
    statusText: ok ? "OK" : "Service Unavailable",
    json: jest.fn().mockResolvedValue(payload)
  };
  global.fetch = jest.fn().mockResolvedValue(response) as unknown as typeof fetch;
  return response;
}

describe("API client", () => {
  beforeEach(() => {
    process.env.NEXT_PUBLIC_API_BASE_URL = "http://api.test";
    jest.restoreAllMocks();
  });

  it("uses cached analytics fetches and normalizes engagement rows by date", async () => {
    mockFetch({
      results: [
        { full_date: "2026-05-02", avg_engagement_rate: 3, total_reach: 200 },
        { full_date: "2026-05-01", avg_engagement_rate: 2, total_reach: 100 }
      ]
    });

    await expect(getEngagement(120)).resolves.toEqual([
      { date: "2026-05-01", engagementRate: 2, reach: 100 },
      { date: "2026-05-02", engagementRate: 3, reach: 200 }
    ]);
    expect(global.fetch).toHaveBeenCalledWith(
      "http://api.test/api/v1/analytics/engagement/?limit=120",
      expect.objectContaining({ next: { revalidate: 900 } })
    );
  });

  it("keeps sync status uncached because it reflects the current warehouse run", async () => {
    mockFetch({
      status: "success",
      source: "etl.cli",
      finished_at: "2026-05-31T00:00:00Z",
      counts: { posts: 876, comments: 1692 },
      freshness: { dataThrough: "2026-05-31", generatedAt: "2026-05-31T00:00:00Z", status: "fresh" }
    });

    const status = await getSyncStatus();

    expect(status.processedPosts).toBe(876);
    expect(global.fetch).toHaveBeenCalledWith(
      "http://api.test/api/v1/sync/status/",
      expect.objectContaining({ cache: "no-store" })
    );
  });

  it("maps competitor BI fields from the warehouse contract", async () => {
    mockFetch({
      results: [
        {
          page_name: "Highlands Coffee Vietnam",
          post_count: 123,
          share_of_voice: 72.5,
          avg_engagement_rate: 2.4,
          sentiment_ratio: 31.8
        }
      ]
    });

    await expect(getCompetitors()).resolves.toEqual([
      {
        brand: "Highlands Coffee Vietnam",
        posts: 123,
        shareOfVoice: 72.5,
        engagementRate: 2.4,
        sentimentRatio: 31.8
      }
    ]);
  });

  it("raises sanitized API details without exposing raw response objects", async () => {
    mockFetch({ detail: "Warehouse unavailable", source_type: "warehouse" }, false);

    await expect(getEngagement()).rejects.toThrow(
      "SocialLens API request failed for /api/v1/analytics/engagement/?limit=120: Warehouse unavailable"
    );
  });
});
