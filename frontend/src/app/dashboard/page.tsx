import { Heatmap } from "@/components/Heatmap";
import { KpiCard } from "@/components/KpiCard";
import { PageHeader } from "@/components/PageHeader";
import { SimpleChart } from "@/components/SimpleChart";
import { getEngagement, getHeatmap, getOverview, getSentiment, getTopPosts } from "@/lib/api";
import { formatNumber, formatPercent } from "@/lib/format";

export default async function DashboardPage() {
  const [overview, engagement, sentiment, heatmap, posts] = await Promise.all([
    getOverview(),
    getEngagement(),
    getSentiment(),
    getHeatmap(),
    getTopPosts()
  ]);
  const topPost = posts[0];

  return (
    <main className="page">
      <PageHeader
        eyebrow={overview.dateRange}
        title="Executive overview"
        description="High-level performance view for engagement, sentiment, virality, reach growth, and share of voice."
      />

      <section className="grid kpi-grid">
        {overview.kpis.map((kpi) => (
          <KpiCard kpi={kpi} key={kpi.label} />
        ))}
      </section>

      <section className="grid two-col">
        <section className="panel insight">
          <div className="panel-header">
            <h2>Key finding</h2>
          </div>
          <strong>{overview.finding.title}</strong>
          <p>{overview.finding.body}</p>
          <p>{overview.finding.action}</p>
          {topPost ? (
            <p>
              Top post: {topPost.message} with {formatNumber(topPost.engagementCount)} engagements
              and {formatPercent(topPost.engagementRate)} engagement rate.
            </p>
          ) : null}
        </section>
        <SimpleChart
          title="Engagement trend"
          points={engagement.map((point) => ({
            label: point.date,
            value: point.engagementRate
          }))}
        />
        <SimpleChart
          title="Positive sentiment"
          points={sentiment.map((point) => ({
            label: point.date,
            value: point.positive
          }))}
        />
        <Heatmap cells={heatmap} />
      </section>
    </main>
  );
}
