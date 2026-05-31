import { DataTable, type Column } from "@/components/DataTable";
import { PageHeader } from "@/components/PageHeader";
import { SimpleChart } from "@/components/SimpleChart";
import { getSentiment } from "@/lib/api";
import { formatPercent } from "@/lib/format";
import { getDictionary } from "@/lib/i18n";
import { getRequestLocale } from "@/lib/i18n-server";
import type { SentimentPoint } from "@/lib/types";

export const revalidate = 900;

export default async function SentimentPage() {
  const locale = await getRequestLocale();
  const dictionary = getDictionary(locale);
  const sentiment = await getSentiment();
  const columns: Column<SentimentPoint>[] = [
    { key: "date", header: dictionary.sentiment.columns.date, render: (row) => row.date },
    { key: "positive", header: dictionary.sentiment.columns.positive, render: (row) => formatPercent(row.positive) },
    { key: "neutral", header: dictionary.sentiment.columns.neutral, render: (row) => formatPercent(row.neutral) },
    { key: "negative", header: dictionary.sentiment.columns.negative, render: (row) => formatPercent(row.negative) }
  ];

  return (
    <main className="page">
      <PageHeader
        eyebrow={dictionary.sentiment.eyebrow}
        title={dictionary.sentiment.title}
        description={dictionary.sentiment.description}
      />
      <section className="grid two-col">
        <SimpleChart
          emptyLabel={dictionary.common.noData}
          title={dictionary.sentiment.positiveRatio}
          points={sentiment.map((row) => ({ label: row.date, value: row.positive }))}
        />
        <SimpleChart
          emptyLabel={dictionary.common.noData}
          title={dictionary.sentiment.negativeRatio}
          points={sentiment.map((row) => ({ label: row.date, value: row.negative }))}
        />
      </section>
      <div style={{ height: 16 }} />
      <DataTable emptyLabel={dictionary.common.noData} title={dictionary.sentiment.tableTitle} columns={columns} rows={sentiment} />
    </main>
  );
}
