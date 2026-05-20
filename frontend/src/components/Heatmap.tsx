import type { HeatmapCell } from "@/lib/types";

type HeatmapProps = {
  cells: HeatmapCell[];
};

export function Heatmap({ cells }: HeatmapProps) {
  const maxValue = Math.max(...cells.map((cell) => cell.engagementRate), 1);

  return (
    <section className="panel">
      <div className="panel-header">
        <h2>Posting time heatmap</h2>
      </div>
      <div className="heatmap">
        {cells.map((cell) => (
          <div
            className="heatmap-cell"
            key={`${cell.day}-${cell.hour}`}
            style={{ opacity: 0.35 + (cell.engagementRate / maxValue) * 0.65 }}
          >
            <span>{cell.day}</span>
            <strong>{cell.hour}:00</strong>
            <small>{cell.engagementRate.toFixed(1)}%</small>
          </div>
        ))}
      </div>
    </section>
  );
}
