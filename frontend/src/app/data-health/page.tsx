import { KpiCard } from "@/components/KpiCard";
import { PageHeader } from "@/components/PageHeader";
import { getSyncStatus } from "@/lib/api";
import { formatDateTime, formatNumber } from "@/lib/format";

export default async function DataHealthPage() {
  const status = await getSyncStatus();

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
            delta: status.source,
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
            label: "Processed posts",
            value: formatNumber(status.processedPosts),
            delta: "dashboard-ready",
            tone: "positive"
          }}
        />
        <KpiCard
          kpi={{
            label: "Processed comments",
            value: formatNumber(status.processedComments),
            delta: status.qualityPassed ? "quality passed" : "review needed",
            tone: status.qualityPassed ? "positive" : "warning"
          }}
        />
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
