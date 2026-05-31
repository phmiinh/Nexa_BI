import { DataTable, type Column } from "@/components/DataTable";
import { PageHeader } from "@/components/PageHeader";
import { SimpleChart } from "@/components/SimpleChart";
import { getContentPerformance } from "@/lib/api";
import { formatNumber, formatPercent } from "@/lib/format";
import { getDictionary } from "@/lib/i18n";
import { getRequestLocale } from "@/lib/i18n-server";
import type { ContentPerformance } from "@/lib/types";

export const revalidate = 900;

export default async function ContentPage() {
  const locale = await getRequestLocale();
  const dictionary = getDictionary(locale);
  const numberLocale = locale === "vi" ? "vi-VN" : "en-US";
  const content = await getContentPerformance();
  const columns: Column<ContentPerformance>[] = [
    { key: "contentType", header: dictionary.content.columns.contentType, render: (row) => row.contentType },
    { key: "posts", header: dictionary.content.columns.posts, render: (row) => formatNumber(row.posts, numberLocale) },
    { key: "reach", header: dictionary.content.columns.reach, render: (row) => formatNumber(row.reach, numberLocale) },
    { key: "engagementRate", header: dictionary.content.columns.engagementRate, render: (row) => formatPercent(row.engagementRate) },
    { key: "viralityScore", header: dictionary.content.columns.viralityScore, render: (row) => formatPercent(row.viralityScore) }
  ];

  return (
    <main className="page">
      <PageHeader
        eyebrow={dictionary.content.eyebrow}
        title={dictionary.content.title}
        description={dictionary.content.description}
      />
      <section className="grid two-col">
        <SimpleChart
          emptyLabel={dictionary.common.noData}
          title={dictionary.content.engagementByType}
          points={content.map((row) => ({ label: row.contentType, value: row.engagementRate }))}
        />
        <SimpleChart
          emptyLabel={dictionary.common.noData}
          title={dictionary.content.viralityByType}
          points={content.map((row) => ({ label: row.contentType, value: row.viralityScore }))}
        />
      </section>
      <div style={{ height: 16 }} />
      <DataTable emptyLabel={dictionary.common.noData} title={dictionary.content.tableTitle} columns={columns} rows={content} />
    </main>
  );
}
