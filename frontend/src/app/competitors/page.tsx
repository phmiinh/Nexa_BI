import { DataTable, type Column } from "@/components/DataTable";
import { PageHeader } from "@/components/PageHeader";
import { SimpleChart } from "@/components/SimpleChart";
import { getCompetitors } from "@/lib/api";
import { formatNumber, formatPercent } from "@/lib/format";
import { getDictionary } from "@/lib/i18n";
import { getRequestLocale } from "@/lib/i18n-server";
import type { Competitor } from "@/lib/types";

export const revalidate = 900;

export default async function CompetitorsPage() {
  const locale = await getRequestLocale();
  const dictionary = getDictionary(locale);
  const numberLocale = locale === "vi" ? "vi-VN" : "en-US";
  const competitors = await getCompetitors();
  const columns: Column<Competitor>[] = [
    { key: "brand", header: dictionary.competitors.columns.brand, render: (row) => row.brand },
    { key: "posts", header: dictionary.competitors.columns.posts, render: (row) => formatNumber(row.posts, numberLocale) },
    { key: "shareOfVoice", header: dictionary.competitors.columns.shareOfVoice, render: (row) => formatPercent(row.shareOfVoice) },
    { key: "engagementRate", header: dictionary.competitors.columns.engagementRate, render: (row) => formatPercent(row.engagementRate) },
    { key: "sentimentRatio", header: dictionary.competitors.columns.sentimentRatio, render: (row) => formatPercent(row.sentimentRatio) }
  ];

  return (
    <main className="page">
      <PageHeader
        eyebrow={dictionary.competitors.eyebrow}
        title={dictionary.competitors.title}
        description={dictionary.competitors.description}
      />
      <section className="grid two-col">
        <SimpleChart
          emptyLabel={dictionary.common.noData}
          title={dictionary.competitors.shareOfVoice}
          points={competitors.map((row) => ({ label: row.brand, value: row.shareOfVoice }))}
        />
        <SimpleChart
          emptyLabel={dictionary.common.noData}
          title={dictionary.competitors.engagementRate}
          points={competitors.map((row) => ({ label: row.brand, value: row.engagementRate }))}
        />
      </section>
      <div style={{ height: 16 }} />
      <DataTable emptyLabel={dictionary.common.noData} title={dictionary.competitors.tableTitle} columns={columns} rows={competitors} />
    </main>
  );
}
