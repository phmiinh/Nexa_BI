import { DataTable, type Column } from "@/components/DataTable";
import { PageHeader } from "@/components/PageHeader";
import { SimpleChart } from "@/components/SimpleChart";
import { getSentiment } from "@/lib/api";
import { formatPercent } from "@/lib/format";
import type { SentimentPoint } from "@/lib/types";

const columns: Column<SentimentPoint>[] = [
  { key: "date", header: "Date", render: (row) => row.date },
  { key: "positive", header: "Positive", render: (row) => formatPercent(row.positive) },
  { key: "neutral", header: "Neutral", render: (row) => formatPercent(row.neutral) },
  { key: "negative", header: "Negative", render: (row) => formatPercent(row.negative) }
];

export default async function SentimentPage() {
  const sentiment = await getSentiment();

  return (
    <main className="page">
      <PageHeader
        eyebrow="Sentiment analysis"
        title="Brand health"
        description="Track positive, neutral, and negative comment ratios over time."
      />
      <section className="grid two-col">
        <SimpleChart
          title="Positive ratio"
          points={sentiment.map((row) => ({ label: row.date, value: row.positive }))}
        />
        <SimpleChart
          title="Negative ratio"
          points={sentiment.map((row) => ({ label: row.date, value: row.negative }))}
        />
      </section>
      <div style={{ height: 16 }} />
      <DataTable title="Sentiment trend table" columns={columns} rows={sentiment} />
    </main>
  );
}
