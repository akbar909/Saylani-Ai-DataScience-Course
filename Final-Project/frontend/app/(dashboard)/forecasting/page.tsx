"use client";

import Link from "next/link";
import { ArrowUpRight, BarChart3, CheckCircle2, DollarSign, Loader2, Sparkles, TrendingUp } from "lucide-react";
import { useEffect, useState } from "react";
import { apiFetch } from "../../../lib/api";

interface Readiness {
  available: boolean;
  message: string;
}

interface ForecastPoint {
  date: string;
  predicted: GLfloat;
  lower_bound: GLfloat;
  upper_bound: GLfloat;
}

interface ForecastResponse {
  metric: string;
  horizon_days: number;
  data: ForecastPoint[];
  summary: {
    total_projected: number;
    daily_average: number;
    model_confidence: number;
  };
}

export default function ForecastingPage() {
  const [readiness, setReadiness] = useState<Readiness | null>(null);
  const [metric, setMetric] = useState<"revenue" | "expenses" | "churn">("revenue");
  const [horizon, setHorizon] = useState<number>(30);
  const [forecast, setForecast] = useState<ForecastResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    apiFetch<Readiness>("/api/v1/forecasts/readiness")
      .then(setReadiness)
      .catch((reason: Error) => setError(reason.message));
  }, []);

  const loadForecast = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await apiFetch<ForecastResponse>("/api/v1/forecasts/predict", {
        method: "POST",
        body: JSON.stringify({ metric, horizon_days: horizon }),
      });
      setForecast(data);
    } catch (err: any) {
      setError(err.message || "Failed to generate forecast.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (readiness?.available) {
      loadForecast();
    }
  }, [readiness, metric, horizon]);

  return (
    <div className="dashboard-page">
      <section className="page-heading">
        <div>
          <span className="eyebrow">Financial Planning Studio</span>
          <h1>AI Forecasting</h1>
          <p>Machine-learning driven forward predictions for revenue, expenses, and churn metrics.</p>
        </div>
        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
          <span className="badge badge-green" style={{ padding: "6px 12px", fontSize: 11 }}>
            <i></i> ML Model Ready
          </span>
        </div>
      </section>

      {/* Control panel & KPI cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 16, marginBottom: 20 }}>
        <article className="kpi-card">
          <div className="kpi-heading">
            <span>METRIC SELECTOR</span>
            <Sparkles size={16} style={{ color: "#42815c" }} />
          </div>
          <div style={{ display: "flex", gap: 6, marginTop: 12 }}>
            <button
              className={`select-button ${metric === "revenue" ? "primary-button" : "outline-button"}`}
              style={{ flex: 1, height: 34 }}
              onClick={() => setMetric("revenue")}
            >
              Revenue
            </button>
            <button
              className={`select-button ${metric === "expenses" ? "primary-button" : "outline-button"}`}
              style={{ flex: 1, height: 34 }}
              onClick={() => setMetric("expenses")}
            >
              Expenses
            </button>
            <button
              className={`select-button ${metric === "churn" ? "primary-button" : "outline-button"}`}
              style={{ flex: 1, height: 34 }}
              onClick={() => setMetric("churn")}
            >
              Churn Rate
            </button>
          </div>
        </article>

        <article className="kpi-card">
          <div className="kpi-heading">
            <span>FORECAST HORIZON</span>
            <TrendingUp size={16} style={{ color: "#42815c" }} />
          </div>
          <div style={{ display: "flex", gap: 6, marginTop: 12 }}>
            {[14, 30, 60, 90].map((h) => (
              <button
                key={h}
                className={`select-button ${horizon === h ? "primary-button" : "outline-button"}`}
                style={{ flex: 1, height: 34 }}
                onClick={() => setHorizon(h)}
              >
                {h} Days
              </button>
            ))}
          </div>
        </article>

        <article className="kpi-card">
          <div className="kpi-heading">
            <span>PROJECTED TOTAL</span>
            <span className="trend trend-up"><ArrowUpRight size={13} /> +8.4%</span>
          </div>
          <strong className="kpi-value">
            {forecast ? (metric === "churn" ? `${forecast.summary.daily_average}%` : `$${forecast.summary.total_projected.toLocaleString()}`) : "—"}
          </strong>
          <span className="kpi-detail">Confidence: {forecast?.summary.model_confidence ?? 95.0}% (Ridge ML Model)</span>
        </article>
      </div>

      {/* Main Forecast Chart & Table Panel */}
      <article className="panel">
        <div className="panel-heading">
          <div>
            <span className="eyebrow">Scoring Output</span>
            <h2>{horizon}-Day {metric.toUpperCase()} Trend Projection</h2>
          </div>
          {loading && <Loader2 size={18} className="spin" style={{ color: "#579271" }} />}
        </div>

        {error ? (
          <div className="form-alert" style={{ marginTop: 20 }}>{error}</div>
        ) : (
          <>
            <div className="chart-area" style={{ height: 210, marginTop: 24 }}>
              <div className="chart-fill" />
              <div className="chart-line" />
              <div className="chart-marker marker-one" />
              <div className="chart-marker marker-two" />
              <div className="chart-labels">
                <span>{forecast?.data[0]?.date ?? "Day 1"}</span>
                <span>{forecast?.data[Math.floor((forecast.data.length - 1) / 2)]?.date ?? "Mid-period"}</span>
                <span>{forecast?.data[forecast.data.length - 1]?.date ?? "End Horizon"}</span>
              </div>
            </div>

            <div style={{ marginTop: 28 }}>
              <h3 style={{ fontSize: 15, fontFamily: "Georgia, serif", marginBottom: 12 }}>Detailed Prediction Breakdown</h3>
              <div className="transaction-table">
                <div className="table-row table-header">
                  <span>DATE</span>
                  <span>PREDICTED</span>
                  <span>CONFIDENCE BAND</span>
                  <span>TREND</span>
                </div>
                {forecast?.data.slice(0, 7).map((pt) => (
                  <div className="table-row" key={pt.date}>
                    <strong>{pt.date}</strong>
                    <span>{metric === "churn" ? `${pt.predicted}%` : `$${pt.predicted.toLocaleString()}`}</span>
                    <span>{metric === "churn" ? `${pt.lower_bound}% – ${pt.upper_bound}%` : `$${pt.lower_bound.toLocaleString()} – $${pt.upper_bound.toLocaleString()}`}</span>
                    <span className="badge badge-green"><i></i> Expected</span>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </article>
    </div>
  );
}

