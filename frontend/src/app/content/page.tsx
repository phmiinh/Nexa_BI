import { DataTable, type Column } from "@/components/DataTable";
import { PageHeader } from "@/components/PageHeader";
import { SimpleChart } from "@/components/SimpleChart";
import { getContentPerformance } from "@/lib/api";
import { formatNumber, formatPercent } from "@/lib/format";
import type { ContentPerformance } from "@/lib/types";

const columns: Column<ContentPerformance>[] = [
  { key: "contentType", header: "Content type", render: (row) => row.contentType },
  { key: "posts", header: "Posts", render: (row) => formatNumber(row.posts) },
  { key: "reach", header: "Reach", render: (row) => formatNumber(row.reach) },
  { key: "engagementRate", header: "Engagement rate", render: (row) => formatPercent(row.engagementRate) },
  { key: "viralityScore", header: "Virality score", render: (row) => formatPercent(row.viralityScore) }
];

export default async function ContentPage() {
  const content = await getContentPerformance();

  return (
    <main className="page">
      <PageHeader
        eyebrow="Content performance"
        title="Content mix"
        description="Compare post formats by reach, engagement rate, and virality score."
      />
      <section className="grid two-col">
        <SimpleChart
          title="Engagement rate by type"
          points={content.map((row) => ({ label: row.contentType, value: row.engagementRate }))}
        />
        <SimpleChart
          title="Virality by type"
          points={content.map((row) => ({ label: row.contentType, value: row.viralityScore }))}
        />
      </section>
      <div style={{ height: 16 }} />
      <DataTable title="Content performance table" columns={columns} rows={content} />
    </main>
  );
}
