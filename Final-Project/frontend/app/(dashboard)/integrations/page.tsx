"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, XCircle } from "lucide-react";
import { apiFetch } from "../../../lib/api";

interface ModelStatus {
  available: boolean;
  [key: string]: string | number | boolean | null;
}

export default function IntegrationsPage() {
  const [health, setHealth] = useState<Record<string, ModelStatus> | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    apiFetch<Record<string, ModelStatus>>("/api/v1/health/models")
      .then(setHealth)
      .catch((caught) => setError(caught instanceof Error ? caught.message : "Unable to fetch integration status."));
  }, []);

  return (
    <div className="dashboard-page">
      <section className="page-heading">
        <div>
          <span className="eyebrow">Connected finance</span>
          <h1>Integrations</h1>
          <p>Track your active connectors and model health from backend services.</p>
        </div>
      </section>

      <article className="panel">
        <div className="panel-heading">
          <div>
            <span className="eyebrow">Model services</span>
            <h2>Service health</h2>
          </div>
        </div>

        {error && <div className="form-alert">{error}</div>}

        {health ? (
          <div className="status-grid">
            {Object.entries(health).map(([name, details]) => {
              const { available, ...rest } = details;
              return (
                <div key={name} className="status-card">
                  <strong>{name.replace(/_/g, " ")}</strong>
                  <span className={`status-badge ${available ? "status-available" : "status-unavailable"}`}>
                    {available ? <CheckCircle2 size={11} /> : <XCircle size={11} />}
                    {available ? "Available" : "Unavailable"}
                  </span>
                  <div className="status-detail">
                    {Object.entries(rest).map(([key, val]) => (
                      <div key={key} className="status-detail-row">
                        <span>{key.replace(/_/g, " ")}</span>
                        <span>{String(val ?? "—")}</span>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          !error && <div className="empty-result compact"><strong>Loading integration status…</strong></div>
        )}
      </article>
    </div>
  );
}
