import type { Kpi } from "@/lib/types";

type KpiCardProps = {
  kpi: Kpi;
};

export function KpiCard({ kpi }: KpiCardProps) {
  return (
    <article className="kpi-card">
      <div className="muted">{kpi.label}</div>
      <div className="kpi-value">{kpi.value}</div>
      <div className={`delta delta-${kpi.tone}`}>{kpi.delta}</div>
    </article>
  );
}
