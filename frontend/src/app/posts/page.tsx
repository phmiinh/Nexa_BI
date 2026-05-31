import { DataTable, type Column } from "@/components/DataTable";
import { PageHeader } from "@/components/PageHeader";
import { getPosts } from "@/lib/api";
import { formatDateTime, formatNumber, formatPercent } from "@/lib/format";
import { getDictionary } from "@/lib/i18n";
import { getRequestLocale } from "@/lib/i18n-server";
import type { Post } from "@/lib/types";

export const revalidate = 900;

export default async function PostsPage() {
  const locale = await getRequestLocale();
  const dictionary = getDictionary(locale);
  const numberLocale = locale === "vi" ? "vi-VN" : "en-US";
  const dateLocale = locale === "vi" ? "vi-VN" : "en-GB";
  const posts = await getPosts(100);
  const columns: Column<Post>[] = [
    { key: "id", header: dictionary.posts.columns.id, render: (row) => row.id },
    { key: "platform", header: dictionary.posts.columns.platform, render: (row) => row.platform },
    { key: "brand", header: dictionary.posts.columns.brand, render: (row) => row.brand },
    { key: "message", header: dictionary.posts.columns.message, render: (row) => row.message },
    { key: "createdAt", header: dictionary.posts.columns.createdAt, render: (row) => formatDateTime(row.createdAt, dateLocale) },
    { key: "reach", header: dictionary.posts.columns.reach, render: (row) => formatNumber(row.reach, numberLocale) },
    { key: "engagementRate", header: dictionary.posts.columns.engagementRate, render: (row) => formatPercent(row.engagementRate) },
    { key: "sentimentRatio", header: dictionary.posts.columns.sentimentRatio, render: (row) => formatPercent(row.sentimentRatio) }
  ];

  return (
    <main className="page">
      <PageHeader
        eyebrow={dictionary.posts.eyebrow}
        title={dictionary.posts.title}
        description={dictionary.posts.description}
      />
      <DataTable
        emptyLabel={dictionary.common.noData}
        title={dictionary.posts.tableTitle}
        columns={columns}
        rows={posts}
        rowKey={(row) => row.id}
      />
    </main>
  );
}
