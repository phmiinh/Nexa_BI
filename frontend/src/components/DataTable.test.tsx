import { render, screen, within } from "@testing-library/react";

import { DataTable, type Column } from "@/components/DataTable";

type Row = {
  id: string;
  brand: string;
  engagementRate: number;
};

const columns: Column<Row>[] = [
  { key: "brand", header: "Brand", render: (row) => row.brand },
  { key: "engagement", header: "Engagement", render: (row) => `${row.engagementRate}%` }
];

describe("DataTable", () => {
  it("renders a clear empty state when the API returns no rows", () => {
    render(<DataTable columns={columns} emptyLabel="No posts matched" rows={[]} title="Posts" />);

    expect(screen.getByRole("heading", { name: "Posts" })).toBeInTheDocument();
    expect(screen.getByText("No posts matched")).toBeInTheDocument();
  });

  it("renders rows with caller-provided stable row keys", () => {
    const rows = [
      { id: "yt_1", brand: "Highlands", engagementRate: 2.5 },
      { id: "yt_2", brand: "Phuc Long", engagementRate: 3.1 }
    ];

    render(<DataTable columns={columns} rowKey={(row) => row.id} rows={rows} title="Competitors" />);

    const bodyRows = within(screen.getAllByRole("rowgroup")[1]).getAllByRole("row");
    expect(bodyRows).toHaveLength(2);
    expect(screen.getByText("Highlands")).toBeInTheDocument();
    expect(screen.getByText("3.1%")).toBeInTheDocument();
  });
});
