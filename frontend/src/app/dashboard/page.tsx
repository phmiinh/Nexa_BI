import { Heatmap } from "@/components/Heatmap";
import { KpiCard } from "@/components/KpiCard";
import { PageHeader } from "@/components/PageHeader";
import { SimpleChart } from "@/components/SimpleChart";
import {
  getEngagement,
  getHeatmap,
  getInsights,
  getOverview,
  getSentiment,
  getTopPosts
} from "@/lib/api";
import { formatNumber, formatPercent } from "@/lib/format";
import { getDictionary } from "@/lib/i18n";
import { getRequestLocale } from "@/lib/i18n-server";

export const revalidate = 900;

export default async function DashboardPage() {
  const locale = await getRequestLocale();
  const dictionary = getDictionary(locale);
  const numberLocale = locale === "vi" ? "vi-VN" : "en-US";
  const [overview, engagement, sentiment, heatmap, posts, insights] = await Promise.all([
    getOverview(locale),
    getEngagement(120),
    getSentiment(120),
    getHeatmap(locale),
    getTopPosts(),
    getInsights(locale)
  ]);
  const topPost = posts[0];

  return (
    <main className="page">
      <PageHeader
        eyebrow={overview.dateRange}
        title={dictionary.dashboard.title}
        description={dictionary.dashboard.description}
      />

      <section className="grid kpi-grid">
        {overview.kpis.map((kpi) => (
          <KpiCard kpi={kpi} key={kpi.label} />
        ))}
      </section>

      <section className="grid two-col">
        <section className="panel insight">
          <div className="panel-header">
            <h2>{dictionary.dashboard.insights}</h2>
            <span className={`badge badge-${insights.freshness.status}`}>{insights.freshness.status}</span>
          </div>
          <strong>{overview.finding.title}</strong>
          <p>{overview.finding.body}</p>
          <p>{overview.finding.action}</p>
          <div className="insight-list">
            {insights.highlights.map((item) => (
              <div className="insight-item" key={item.title}>
                <span className={`delta delta-${item.tone}`}>{item.metric || item.title}</span>
                <p>{item.detail}</p>
              </div>
            ))}
          </div>
          <div className="source-meta">
            <span>
              {dictionary.common.dataThrough} {insights.freshness.dataThrough}
            </span>
            <span>
              {insights.sourceConfidence.level} {dictionary.common.confidenceFrom} {insights.source}
            </span>
          </div>
          {topPost ? (
            <p>
              {dictionary.common.topPost}: {topPost.brand} {topPost.contentType} {dictionary.common.with}{" "}
              {formatNumber(topPost.engagementCount, numberLocale)} {dictionary.common.engagements} {dictionary.common.and}{" "}
              {formatPercent(topPost.engagementRate)} {dictionary.common.engagementRate}.
            </p>
          ) : null}
        </section>
        <SimpleChart
          emptyLabel={dictionary.common.noData}
          title={dictionary.dashboard.engagementTrend}
          points={engagement.map((point) => ({
            label: point.date,
            value: point.engagementRate
          }))}
        />
        <SimpleChart
          emptyLabel={dictionary.common.noData}
          title={dictionary.dashboard.positiveSentiment}
          points={sentiment.map((point) => ({
            label: point.date,
            value: point.positive
          }))}
        />
        <Heatmap cells={heatmap} emptyLabel={dictionary.common.noData} title={dictionary.heatmap.title} />
      </section>
    </main>
  );
}
