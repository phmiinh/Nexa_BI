export default function LoadingPage() {
  return (
    <main className="page">
      <section className="panel status-panel">
        <p className="eyebrow">Loading</p>
        <h1>Loading BI dashboard data</h1>
        <p>Reading the latest PostgreSQL warehouse snapshot.</p>
      </section>
    </main>
  );
}
