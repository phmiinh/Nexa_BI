import { KpiCard } from "@/components/KpiCard";
import { PageHeader } from "@/components/PageHeader";
import { getInsights, getSyncStatus } from "@/lib/api";
import { formatDateTime, formatNumber } from "@/lib/format";

export default async function DataHealthPage() {
  const [status, insights] = await Promise.all([getSyncStatus(), getInsights()]);
  const confidenceTone = insights.sourceConfidence.level === "low" ? "warning" : "positive";

  return (
    <main className="page">
      <PageHeader
        eyebrow="Data health"
        title="Pipeline status"
        description="Monitor sync source, processed row counts, and validation checks for dashboard readiness."
      />
      <section className="grid kpi-grid">
        <KpiCard
          kpi={{
            label: "Sync mode",
            value: status.status,
            delta: `source: ${status.source}`,
            tone: status.status === "fallback" ? "warning" : "positive"
          }}
        />
        <KpiCard
          kpi={{
            label: "Last run",
            value: formatDateTime(status.lastRunAt),
            delta: "Asia/Ho_Chi_Minh",
            tone: "neutral"
          }}
        />
        <KpiCard
          kpi={{
            label: "Data through",
            value: status.freshness.dataThrough,
            delta: status.freshness.status,
            tone: status.freshness.status === "fresh" ? "positive" : "warning"
          }}
        />
        <KpiCard
          kpi={{
            label: "Source confidence",
            value: `${Math.round(status.sourceConfidence.score * 100)}%`,
            delta: status.sourceConfidence.level,
            tone: status.sourceConfidence.level === "low" ? "warning" : "positive"
          }}
        />
      </section>
      <section className="grid two-col health-grid">
        <section className="panel">
          <div className="panel-header">
            <h2>Data freshness</h2>
            <span className={`badge badge-${status.freshness.status}`}>{status.freshness.status}</span>
          </div>
          <div className="metric-list">
            <div>
              <span>Processed posts</span>
              <strong>{formatNumber(status.processedPosts)}</strong>
            </div>
            <div>
              <span>Processed comments</span>
              <strong>{formatNumber(status.processedComments)}</strong>
            </div>
            <div>
              <span>Snapshot generated</span>
              <strong>{formatDateTime(insights.generatedAt)}</strong>
            </div>
          </div>
        </section>
        <section className="panel insight">
          <div className="panel-header">
            <h2>Source confidence</h2>
            <span className={`delta delta-${confidenceTone}`}>{insights.sourceConfidence.level}</span>
          </div>
          <p>{insights.sourceConfidence.detail}</p>
          <div className="insight-list">
            {insights.risks.map((risk) => (
              <div className="insight-item" key={risk.title}>
                <span className={`delta delta-${risk.tone}`}>{risk.title}</span>
                <p>{risk.detail}</p>
              </div>
            ))}
          </div>
        </section>
      </section>
      <section className="panel">
        <div className="panel-header">
          <h2>Quality checks</h2>
        </div>
        <div className="status-list">
          {status.checks.map((check) => (
            <div className="status-item" key={check.name}>
              <div>
                <strong>{check.name}</strong>
                <span>{check.detail}</span>
              </div>
              <span className={`badge badge-${check.status}`}>{check.status}</span>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
