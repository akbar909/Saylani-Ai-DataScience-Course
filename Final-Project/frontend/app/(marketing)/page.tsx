import Link from "next/link";

export default function HomePage() {
  return (
    <main className="marketing-page">
      <span className="eyebrow">AI finance workspace</span>
      <h1>Modern finance intelligence for high-growth teams.</h1>
      <p className="marketing-copy">
        Ledgerly brings forecasting, fraud scoring, and document intelligence into a single secure dashboard so finance leaders can act with confidence.
      </p>
      <div className="marketing-actions">
        <Link href="/signup" className="topbar-upload">
          Start free
        </Link>
        <Link href="/pricing" className="outline-button">
          See pricing
        </Link>
      </div>
    </main>
  );
}
