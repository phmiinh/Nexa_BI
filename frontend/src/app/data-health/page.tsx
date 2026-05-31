import { KpiCard } from "@/components/KpiCard";
import { PageHeader } from "@/components/PageHeader";
import { getInsights, getSyncStatus } from "@/lib/api";
import { formatDateTime, formatNumber } from "@/lib/format";
import { getDictionary } from "@/lib/i18n";
import { getRequestLocale } from "@/lib/i18n-server";

export const revalidate = 900;

export default async function DataHealthPage() {
  const locale = await getRequestLocale();
  const dictionary = getDictionary(locale);
  const numberLocale = locale === "vi" ? "vi-VN" : "en-US";
  const dateLocale = locale === "vi" ? "vi-VN" : "en-GB";
  const [status, insights] = await Promise.all([getSyncStatus(), getInsights(locale)]);
  const confidenceTone = insights.sourceConfidence.level === "low" ? "warning" : "positive";

  return (
    <main className="page">
      <PageHeader
        eyebrow={dictionary.dataHealth.eyebrow}
        title={dictionary.dataHealth.title}
        description={dictionary.dataHealth.description}
      />
      <section className="grid kpi-grid">
        <KpiCard
          kpi={{
            label: dictionary.dataHealth.syncMode,
            value: status.status,
            delta: `${dictionary.dataHealth.source}: ${status.source}`,
            tone: status.status === "success" || status.status === "available" ? "positive" : "warning"
          }}
        />
        <KpiCard
          kpi={{
            label: dictionary.dataHealth.lastRun,
            value: formatDateTime(status.lastRunAt, dateLocale),
            delta: dictionary.dataHealth.timezone,
            tone: "neutral"
          }}
        />
        <KpiCard
          kpi={{
            label: dictionary.dataHealth.dataThrough,
            value: status.freshness.dataThrough,
            delta: status.freshness.status,
            tone: status.freshness.status === "fresh" ? "positive" : "warning"
          }}
        />
        <KpiCard
          kpi={{
            label: dictionary.dataHealth.sourceConfidence,
            value: `${Math.round(status.sourceConfidence.score * 100)}%`,
            delta: status.sourceConfidence.level,
            tone: status.sourceConfidence.level === "low" ? "warning" : "positive"
          }}
        />
      </section>
      <section className="grid two-col health-grid">
        <section className="panel">
          <div className="panel-header">
            <h2>{dictionary.dataHealth.dataFreshness}</h2>
            <span className={`badge badge-${status.freshness.status}`}>{status.freshness.status}</span>
          </div>
          <div className="metric-list">
            <div>
              <span>{dictionary.dataHealth.processedPosts}</span>
              <strong>{formatNumber(status.processedPosts, numberLocale)}</strong>
            </div>
            <div>
              <span>{dictionary.dataHealth.processedComments}</span>
              <strong>{formatNumber(status.processedComments, numberLocale)}</strong>
            </div>
            <div>
              <span>{dictionary.dataHealth.snapshotGenerated}</span>
              <strong>{formatDateTime(insights.generatedAt, dateLocale)}</strong>
            </div>
          </div>
        </section>
        <section className="panel insight">
          <div className="panel-header">
            <h2>{dictionary.dataHealth.sourceConfidence}</h2>
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
          <h2>{dictionary.dataHealth.qualityChecks}</h2>
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
