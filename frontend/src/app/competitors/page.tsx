import { DataTable, type Column } from "@/components/DataTable";
import { PageHeader } from "@/components/PageHeader";
import { SimpleChart } from "@/components/SimpleChart";
import { getCompetitors } from "@/lib/api";
import { formatNumber, formatPercent } from "@/lib/format";
import type { Competitor } from "@/lib/types";

const columns: Column<Competitor>[] = [
  { key: "brand", header: "Brand", render: (row) => row.brand },
  { key: "posts", header: "Posts", render: (row) => formatNumber(row.posts) },
  { key: "shareOfVoice", header: "Share of voice", render: (row) => formatPercent(row.shareOfVoice) },
  { key: "engagementRate", header: "Engagement rate", render: (row) => formatPercent(row.engagementRate) },
  { key: "sentimentRatio", header: "Sentiment ratio", render: (row) => formatPercent(row.sentimentRatio) }
];

export default async function CompetitorsPage() {
  const competitors = await getCompetitors();

  return (
    <main className="page">
      <PageHeader
        eyebrow="Competitor benchmarking"
        title="Share of voice"
        description="Benchmark Highlands Coffee against Phuc Long and The Coffee House."
      />
      <section className="grid two-col">
        <SimpleChart
          title="Share of voice"
          points={competitors.map((row) => ({ label: row.brand, value: row.shareOfVoice }))}
        />
        <SimpleChart
          title="Engagement rate"
          points={competitors.map((row) => ({ label: row.brand, value: row.engagementRate }))}
        />
      </section>
      <div style={{ height: 16 }} />
      <DataTable title="Competitor table" columns={columns} rows={competitors} />
    </main>
  );
}
