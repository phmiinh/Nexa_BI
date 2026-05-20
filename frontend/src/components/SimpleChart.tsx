type ChartPoint = {
  label: string;
  value: number;
};

type SimpleChartProps = {
  title: string;
  points: ChartPoint[];
  unit?: string;
};

export function SimpleChart({ title, points, unit = "%" }: SimpleChartProps) {
  const maxValue = Math.max(...points.map((point) => point.value), 1);

  return (
    <section className="panel">
      <div className="panel-header">
        <h2>{title}</h2>
      </div>
      <div className="bar-chart" aria-label={title}>
        {points.map((point) => (
          <div className="bar-row" key={point.label}>
            <span className="bar-label">{point.label}</span>
            <div className="bar-track">
              <div className="bar-fill" style={{ width: `${(point.value / maxValue) * 100}%` }} />
            </div>
            <span className="bar-value">
              {point.value.toFixed(1)}
              {unit}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}
