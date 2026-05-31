"use client";

export default function ErrorPage({ error: _error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <main className="page">
      <section className="panel status-panel">
        <p className="eyebrow">Data unavailable</p>
        <h1>Unable to load BI dashboard data</h1>
        <p>The PostgreSQL-backed API did not return the required dashboard data. Check the API server and try again.</p>
        <button className="primary-action" type="button" onClick={() => reset()}>
          Retry
        </button>
      </section>
    </main>
  );
}
