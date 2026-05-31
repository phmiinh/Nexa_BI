import type { HeatmapCell } from "@/lib/types";

type HeatmapProps = {
  cells: HeatmapCell[];
  title: string;
  emptyLabel?: string;
};

export function Heatmap({ cells, title, emptyLabel = "No data available" }: HeatmapProps) {
  const maxValue = Math.max(...cells.map((cell) => cell.engagementRate), 1);

  return (
    <section className="panel">
      <div className="panel-header">
        <h2>{title}</h2>
      </div>
      {cells.length ? (
        <div className="heatmap">
          {cells.map((cell, index) => (
            <div
              className="heatmap-cell"
              key={`${cell.day}-${cell.hour}-${index}`}
              style={{ opacity: 0.35 + (cell.engagementRate / maxValue) * 0.65 }}
            >
              <span>{cell.day}</span>
              <strong>{cell.hour}:00</strong>
              <small>{cell.engagementRate.toFixed(1)}%</small>
            </div>
          ))}
        </div>
      ) : (
        <p className="empty-state">{emptyLabel}</p>
      )}
    </section>
  );
}
