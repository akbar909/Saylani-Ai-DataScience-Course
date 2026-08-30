"use client";

import { useEffect, useState } from "react";
import { Check, CheckCircle2, CreditCard, Loader2, Sparkles, Zap } from "lucide-react";
import { apiFetch } from "../../../lib/api";

interface BillingStatus {
  plan: string;
  status: string;
  stripe_configured: boolean;
}

interface SessionResponse {
  checkout_url: string;
  session_id: string;
  demo_mode: boolean;
}

export default function BillingPage() {
  const [billing, setBilling] = useState<BillingStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    apiFetch<BillingStatus>("/api/v1/billing/status")
      .then(setBilling)
      .catch((reason: Error) => setError(reason.message));

    const params = new URLSearchParams(window.location.search);
    if (params.get("success") === "true") {
      setMessage("Subscription updated successfully! Welcome to Pro.");
    } else if (params.get("checkout") === "demo_success") {
      setMessage("Demo Mode: Checkout process simulated successfully!");
    }
  }, []);

  const handleUpgrade = async (planName: string) => {
    setLoading(true);
    setError("");
    setMessage("");
    try {
      const res = await apiFetch<SessionResponse>("/api/v1/billing/create-checkout-session", {
        method: "POST",
        body: JSON.stringify({ plan: planName.toLowerCase() }),
      });
      if (res.checkout_url) {
        window.location.href = res.checkout_url;
      }
    } catch (err: any) {
      setError(err.message || "Failed to start checkout session.");
    } finally {
      setLoading(false);
    }
  };

  const handleManage = async () => {
    setLoading(true);
    try {
      const res = await apiFetch<SessionResponse>("/api/v1/billing/create-portal-session", {
        method: "POST",
      });
      if (res.checkout_url) {
        window.location.href = res.checkout_url;
      }
    } catch (err: any) {
      setError(err.message || "Failed to open customer portal.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard-page">
      <section className="page-heading">
        <div>
          <span className="eyebrow">Workspace plan &amp; subscription</span>
          <h1>Billing &amp; Payments</h1>
          <p>Manage subscription tier, Stripe payment integrations, and workspace limits.</p>
        </div>
      </section>

      {message && (
        <div style={{ marginBottom: 20, padding: 14, borderRadius: 8, background: "#e1f0e3", color: "#2d6143", fontWeight: 600, display: "flex", alignItems: "center", gap: 8 }}>
          <CheckCircle2 size={18} />
          <span>{message}</span>
        </div>
      )}

      {error && (
        <div className="form-alert" style={{ marginBottom: 20 }}>{error}</div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: 20, marginBottom: 28 }}>
        {/* Starter Plan */}
        <article className="panel" style={{ border: billing?.plan === "starter" ? "2px solid #579271" : undefined }}>
          <div className="panel-heading">
            <div>
              <span className="eyebrow">Starter</span>
              <h2 style={{ fontSize: 28 }}>$0 <span style={{ fontSize: 13, color: "#78857d" }}>/month</span></h2>
            </div>
            <CreditCard size={22} className="panel-icon" />
          </div>
          <p style={{ marginTop: 10, color: "#65746b", fontSize: 13 }}>Essential analytics and baseline model checks for small teams.</p>
          <ul style={{ margin: "20px 0", paddingLeft: 0, listStyle: "none", display: "flex", flexDirection: "column", gap: 10, fontSize: 13, color: "#405148" }}>
            <li style={{ display: "flex", alignItems: "center", gap: 8 }}><Check size={15} style={{ color: "#579271" }} /> Baseline Fraud Detection</li>
            <li style={{ display: "flex", alignItems: "center", gap: 8 }}><Check size={15} style={{ color: "#579271" }} /> 50 Document Chat Queries/mo</li>
            <li style={{ display: "flex", alignItems: "center", gap: 8 }}><Check size={15} style={{ color: "#579271" }} /> Standard Overview Analytics</li>
          </ul>
          <button className="outline-button" style={{ width: "100%" }} disabled={billing?.plan === "starter"}>
            {billing?.plan === "starter" ? "Current Plan" : "Downgrade to Starter"}
          </button>
        </article>

        {/* Pro Plan */}
        <article className="panel" style={{ border: "2px solid #3d815b", background: "linear-gradient(180deg, #f3f9f4 0%, #fbfcfa 100%)", position: "relative" }}>
          <div style={{ position: "absolute", top: -11, right: 20, background: "#173b32", color: "#cfe8d7", fontSize: 10, fontWeight: 800, padding: "3px 9px", borderRadius: 12, letterSpacing: ".08em", display: "flex", alignItems: "center", gap: 4 }}>
            <Sparkles size={11} /> MOST POPULAR
          </div>
          <div className="panel-heading">
            <div>
              <span className="eyebrow" style={{ color: "#3d815b" }}>Pro Intelligence</span>
              <h2 style={{ fontSize: 28 }}>$49 <span style={{ fontSize: 13, color: "#78857d" }}>/month</span></h2>
            </div>
            <Zap size={22} style={{ color: "#3d815b" }} />
          </div>
          <p style={{ marginTop: 10, color: "#65746b", fontSize: 13 }}>Full AI capability, forecasting models, and unlimited document chat.</p>
          <ul style={{ margin: "20px 0", paddingLeft: 0, listStyle: "none", display: "flex", flexDirection: "column", gap: 10, fontSize: 13, color: "#405148" }}>
            <li style={{ display: "flex", alignItems: "center", gap: 8 }}><Check size={15} style={{ color: "#579271" }} /> ML Financial Forecasting Studio</li>
            <li style={{ display: "flex", alignItems: "center", gap: 8 }}><Check size={15} style={{ color: "#579271" }} /> Real-time Fraud Detection Scoring</li>
            <li style={{ display: "flex", alignItems: "center", gap: 8 }}><Check size={15} style={{ color: "#579271" }} /> Autonomous AI Financial Agent</li>
            <li style={{ display: "flex", alignItems: "center", gap: 8 }}><Check size={15} style={{ color: "#579271" }} /> Unlimited RAG Document Chat</li>
          </ul>
          <button className="primary-button" style={{ width: "100%" }} onClick={() => handleUpgrade("pro")} disabled={loading}>
            {loading ? <Loader2 size={16} className="spin" /> : "Upgrade to Pro"}
          </button>
        </article>
      </div>

      <article className="panel">
        <div className="panel-heading">
          <div>
            <span className="eyebrow">Integration Status</span>
            <h2>Stripe Gateway Configuration</h2>
          </div>
        </div>
        <div style={{ marginTop: 14, fontSize: 13, color: "#65746b", display: "flex", flexDirection: "column", gap: 10 }}>
          <p>
            Stripe Status:{" "}
            {billing?.stripe_configured ? (
              <span style={{ color: "#3d7a56", fontWeight: 700 }}>● Connected &amp; Live</span>
            ) : (
              <span style={{ color: "#b98536", fontWeight: 700 }}>● Demo Mode (Set STRIPE_SECRET_KEY in backend/.env for production live payments)</span>
            )}
          </p>
          <div>
            <button className="outline-button" onClick={handleManage} disabled={loading}>
              Manage Billing &amp; Invoices
            </button>
          </div>
        </div>
      </article>
    </div>
  );
}

