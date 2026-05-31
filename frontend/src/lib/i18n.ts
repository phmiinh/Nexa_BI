export type Locale = "en" | "vi";

export const defaultLocale: Locale = "en";
export const locales: Locale[] = ["en", "vi"];

export function isLocale(value: string | undefined): value is Locale {
  return value === "en" || value === "vi";
}

export function getDictionary(locale: Locale) {
  return dictionaries[locale];
}

const dictionaries = {
  en: {
    language: {
      label: "Language",
      english: "EN",
      vietnamese: "VI"
    },
    nav: {
      ariaLabel: "Primary navigation",
      dashboard: "Dashboard",
      content: "Content",
      sentiment: "Sentiment",
      competitors: "Competitors",
      posts: "Posts",
      dataHealth: "Data health"
    },
    common: {
      noData: "No data available",
      dataThrough: "Data through",
      confidenceFrom: "confidence from",
      topPost: "Top post",
      with: "with",
      and: "and",
      engagements: "engagements",
      engagementRate: "engagement rate",
      warehouse: "warehouse",
      average: "avg",
      sqlValidated: "SQL validated",
      days: {
        Monday: "Monday",
        Tuesday: "Tuesday",
        Wednesday: "Wednesday",
        Thursday: "Thursday",
        Friday: "Friday",
        Saturday: "Saturday",
        Sunday: "Sunday"
      }
    },
    overview: {
      dateRangeFallback: "Processed dataset",
      kpis: {
        totalEngagement: "Total engagement",
        engagementRate: "Engagement rate",
        viralityScore: "Virality score",
        totalReach: "Total reach"
      },
      finding: {
        title: "Warehouse metrics are available",
        body: "Dashboard values are loaded from SocialLens BI processed data or PostgreSQL views.",
        action: "Use Power BI and SQL validation queries to confirm the final submission metrics."
      }
    },
    dashboard: {
      title: "Executive overview",
      eyebrowFallback: "Executive overview",
      description:
        "High-level performance view for engagement, sentiment, virality, reach growth, and share of voice.",
      insights: "BI insights",
      engagementTrend: "Engagement trend",
      positiveSentiment: "Positive sentiment",
      insightTitles: {
        overview: "Performance summary",
        top_post: "Leading video",
        content: "Content format signal",
        sentiment: "Sentiment signal"
      },
      insightDetails: {
        overview: "Performance summary is available from the current analytics source.",
        top_post: "The leading video is identified by engagement and virality metrics.",
        content: "Content format performance is ranked by engagement rate and total engagement.",
        sentiment: "Comment sentiment distribution is available for brand health tracking."
      }
    },
    content: {
      eyebrow: "Content performance",
      title: "Content mix",
      description: "Compare post formats by reach, engagement rate, and virality score.",
      engagementByType: "Engagement rate by type",
      viralityByType: "Virality by type",
      tableTitle: "Content performance table",
      columns: {
        contentType: "Content type",
        posts: "Posts",
        reach: "Reach",
        engagementRate: "Engagement rate",
        viralityScore: "Virality score"
      }
    },
    sentiment: {
      eyebrow: "Sentiment analysis",
      title: "Brand health",
      description: "Track positive, neutral, and negative comment ratios over time.",
      positiveRatio: "Positive ratio",
      negativeRatio: "Negative ratio",
      tableTitle: "Sentiment trend table",
      columns: {
        date: "Date",
        positive: "Positive",
        neutral: "Neutral",
        negative: "Negative"
      }
    },
    competitors: {
      eyebrow: "Competitor benchmarking",
      title: "Share of voice",
      description: "Benchmark Highlands Coffee against Phuc Long and The Coffee House.",
      shareOfVoice: "Share of voice",
      engagementRate: "Engagement rate",
      tableTitle: "Competitor table",
      columns: {
        brand: "Brand",
        posts: "Posts",
        shareOfVoice: "Share of voice",
        engagementRate: "Engagement rate",
        sentimentRatio: "Sentiment ratio"
      }
    },
    posts: {
      eyebrow: "Post detail",
      title: "Top posts",
      description: "Review post-level reach, engagement count, virality score, and sentiment ratio.",
      tableTitle: "Post performance table",
      columns: {
        id: "Post",
        platform: "Platform",
        brand: "Brand",
        message: "Message",
        createdAt: "VN time",
        reach: "Reach",
        engagementRate: "Engagement rate",
        sentimentRatio: "Sentiment"
      }
    },
    dataHealth: {
      eyebrow: "Data health",
      title: "Pipeline status",
      description: "Monitor sync source, processed row counts, and validation checks for dashboard readiness.",
      syncMode: "Sync mode",
      source: "source",
      lastRun: "Last run",
      timezone: "Asia/Ho_Chi_Minh",
      dataThrough: "Data through",
      sourceConfidence: "Source confidence",
      dataFreshness: "Data freshness",
      processedPosts: "Processed posts",
      processedComments: "Processed comments",
      snapshotGenerated: "Snapshot generated",
      qualityChecks: "Quality checks"
    },
    heatmap: {
      title: "Posting time heatmap"
    }
  },
  vi: {
    language: {
      label: "Ngôn ngữ",
      english: "EN",
      vietnamese: "VI"
    },
    nav: {
      ariaLabel: "Điều hướng chính",
      dashboard: "Tổng quan",
      content: "Nội dung",
      sentiment: "Cảm xúc",
      competitors: "Đối thủ",
      posts: "Bài đăng",
      dataHealth: "Dữ liệu"
    },
    common: {
      noData: "Chưa có dữ liệu",
      dataThrough: "Dữ liệu đến",
      confidenceFrom: "độ tin cậy từ",
      topPost: "Bài nổi bật",
      with: "với",
      and: "và",
      engagements: "lượt tương tác",
      engagementRate: "tỷ lệ tương tác",
      warehouse: "kho dữ liệu",
      average: "trung bình",
      sqlValidated: "Đã kiểm tra SQL",
      days: {
        Monday: "Thứ hai",
        Tuesday: "Thứ ba",
        Wednesday: "Thứ tư",
        Thursday: "Thứ năm",
        Friday: "Thứ sáu",
        Saturday: "Thứ bảy",
        Sunday: "Chủ nhật"
      }
    },
    overview: {
      dateRangeFallback: "Bộ dữ liệu đã xử lý",
      kpis: {
        totalEngagement: "Tổng tương tác",
        engagementRate: "Tỷ lệ tương tác",
        viralityScore: "Điểm lan truyền",
        totalReach: "Tổng tiếp cận"
      },
      finding: {
        title: "Chỉ số từ kho dữ liệu đã sẵn sàng",
        body: "Dashboard đang lấy dữ liệu từ dữ liệu đã xử lý của SocialLens BI hoặc các view PostgreSQL.",
        action: "Dùng Power BI và truy vấn SQL validation để đối chiếu số liệu nộp bài."
      }
    },
    dashboard: {
      title: "Tổng quan điều hành",
      eyebrowFallback: "Tổng quan điều hành",
      description:
        "Theo dõi nhanh tương tác, cảm xúc, độ lan truyền, tăng trưởng tiếp cận và thị phần thảo luận.",
      insights: "Nhận định BI",
      engagementTrend: "Xu hướng tương tác",
      positiveSentiment: "Cảm xúc tích cực",
      insightTitles: {
        overview: "Tổng quan hiệu suất",
        top_post: "Video nổi bật",
        content: "Tín hiệu định dạng nội dung",
        sentiment: "Tín hiệu cảm xúc"
      },
      insightDetails: {
        overview: "Tổng quan hiệu suất đã được lấy từ nguồn phân tích hiện tại.",
        top_post: "Video dẫn đầu được xác định theo tương tác và chỉ số lan truyền.",
        content: "Hiệu quả định dạng nội dung được xếp theo tỷ lệ tương tác và tổng tương tác.",
        sentiment: "Phân bổ cảm xúc bình luận đã sẵn sàng để theo dõi sức khỏe thương hiệu."
      }
    },
    content: {
      eyebrow: "Hiệu quả nội dung",
      title: "Cơ cấu nội dung",
      description: "So sánh định dạng bài đăng theo tiếp cận, tỷ lệ tương tác và điểm lan truyền.",
      engagementByType: "Tỷ lệ tương tác theo loại",
      viralityByType: "Lan truyền theo loại",
      tableTitle: "Bảng hiệu quả nội dung",
      columns: {
        contentType: "Loại nội dung",
        posts: "Số bài",
        reach: "Tiếp cận",
        engagementRate: "Tỷ lệ tương tác",
        viralityScore: "Điểm lan truyền"
      }
    },
    sentiment: {
      eyebrow: "Phân tích cảm xúc",
      title: "Sức khỏe thương hiệu",
      description: "Theo dõi tỷ lệ bình luận tích cực, trung lập và tiêu cực theo thời gian.",
      positiveRatio: "Tỷ lệ tích cực",
      negativeRatio: "Tỷ lệ tiêu cực",
      tableTitle: "Bảng xu hướng cảm xúc",
      columns: {
        date: "Ngày",
        positive: "Tích cực",
        neutral: "Trung lập",
        negative: "Tiêu cực"
      }
    },
    competitors: {
      eyebrow: "So sánh đối thủ",
      title: "Thị phần thảo luận",
      description: "So sánh Highlands Coffee với Phuc Long và The Coffee House.",
      shareOfVoice: "Thị phần thảo luận",
      engagementRate: "Tỷ lệ tương tác",
      tableTitle: "Bảng đối thủ",
      columns: {
        brand: "Thương hiệu",
        posts: "Số bài",
        shareOfVoice: "Thị phần thảo luận",
        engagementRate: "Tỷ lệ tương tác",
        sentimentRatio: "Tỷ lệ cảm xúc"
      }
    },
    posts: {
      eyebrow: "Chi tiết bài đăng",
      title: "Bài đăng nổi bật",
      description: "Xem tiếp cận, tương tác, điểm lan truyền và cảm xúc ở cấp bài đăng.",
      tableTitle: "Bảng hiệu quả bài đăng",
      columns: {
        id: "Bài đăng",
        platform: "Nền tảng",
        brand: "Thương hiệu",
        message: "Nội dung",
        createdAt: "Giờ VN",
        reach: "Tiếp cận",
        engagementRate: "Tỷ lệ tương tác",
        sentimentRatio: "Cảm xúc"
      }
    },
    dataHealth: {
      eyebrow: "Sức khỏe dữ liệu",
      title: "Trạng thái pipeline",
      description: "Theo dõi nguồn đồng bộ, số dòng đã xử lý và kiểm tra chất lượng cho dashboard.",
      syncMode: "Chế độ đồng bộ",
      source: "nguồn",
      lastRun: "Lần chạy cuối",
      timezone: "Asia/Ho_Chi_Minh",
      dataThrough: "Dữ liệu đến",
      sourceConfidence: "Độ tin cậy nguồn",
      dataFreshness: "Độ mới dữ liệu",
      processedPosts: "Bài đã xử lý",
      processedComments: "Bình luận đã xử lý",
      snapshotGenerated: "Snapshot tạo lúc",
      qualityChecks: "Kiểm tra chất lượng"
    },
    heatmap: {
      title: "Heatmap thời điểm đăng"
    }
  }
} as const;
