"use client";

import { useEffect, useState } from "react";
import { FileText } from "lucide-react";
import { apiFetch } from "../../../lib/api";

interface Overview {
  models: Record<string, unknown>;
  transactions: Array<Record<string, string>>;
  signals: Array<{ title: string; description: string }>;
}

export default function ReportsPage() {
  const [overview, setOverview] = useState<Overview | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    apiFetch<Overview>("/api/v1/overview")
      .then(setOverview)
      .catch((caught) => setError(caught instanceof Error ? caught.message : "Unable to load reports."));
  }, []);

  return (
    <div className="dashboard-page">
      <section className="page-heading">
        <div>
          <span className="eyebrow">Reporting workspace</span>
          <h1>Reports</h1>
          <p>Generate summary reports from backend signals and transaction activity.</p>
        </div>
      </section>

      <article className="panel">
        <div className="panel-heading">
          <div>
            <span className="eyebrow">Backend summary</span>
            <h2>Latest snapshot</h2>
          </div>
          <FileText size={21} className="panel-icon" />
        </div>

        {error && <div className="form-alert">{error}</div>}

        {overview ? (
          <>
            <div className="summary-grid">
              <div>
                <strong>Model artifacts</strong>
                <p>{Object.keys(overview.models).length}</p>
              </div>
              <div>
                <strong>Signals</strong>
                <p>{overview.signals.length}</p>
              </div>
              <div>
                <strong>Transactions</strong>
                <p>{overview.transactions.length}</p>
              </div>
            </div>

            {overview.signals.length > 0 ? (
              <div className="report-list">
                {overview.signals.map((signal, index) => (
                  <div key={index} className="report-row">
                    <strong>{signal.title}</strong>
                    <p>{signal.description}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-result compact">
                <strong>No signals to report</strong>
                <span>Connect MongoDB-backed transactions to populate this feed.</span>
              </div>
            )}
          </>
        ) : (
          !error && <div className="empty-result compact"><strong>Loading reporting data…</strong></div>
        )}
      </article>
    </div>
  );
}
