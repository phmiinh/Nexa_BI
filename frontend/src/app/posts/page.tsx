import { DataTable, type Column } from "@/components/DataTable";
import { PageHeader } from "@/components/PageHeader";
import { getPosts } from "@/lib/api";
import { formatDateTime, formatNumber, formatPercent } from "@/lib/format";
import type { Post } from "@/lib/types";

const columns: Column<Post>[] = [
  { key: "id", header: "Post", render: (row) => row.id },
  { key: "platform", header: "Platform", render: (row) => row.platform },
  { key: "brand", header: "Brand", render: (row) => row.brand },
  { key: "message", header: "Message", render: (row) => row.message },
  { key: "createdAt", header: "VN time", render: (row) => formatDateTime(row.createdAt) },
  { key: "reach", header: "Reach", render: (row) => formatNumber(row.reach) },
  { key: "engagementRate", header: "Engagement rate", render: (row) => formatPercent(row.engagementRate) },
  { key: "sentimentRatio", header: "Sentiment", render: (row) => formatPercent(row.sentimentRatio) }
];

export default async function PostsPage() {
  const posts = await getPosts();

  return (
    <main className="page">
      <PageHeader
        eyebrow="Post detail"
        title="Top posts"
        description="Review post-level reach, engagement count, virality score, and sentiment ratio."
      />
      <DataTable title="Post performance table" columns={columns} rows={posts} />
    </main>
  );
}
