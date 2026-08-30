"use client";

import { FormEvent, useState } from "react";
import { AlertTriangle, ArrowUpRight, CheckCircle2, LoaderCircle, ShieldCheck } from "lucide-react";

import { Badge } from "../../../components/ui/Badge";
import { apiFetch } from "../../../lib/api";

export default function FraudDetectionPage() {
  const [mode, setMode] = useState<"credit-card" | "paysim">("credit-card");
  const [features, setFeatures] = useState("0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0");
  const [amount, setAmount] = useState("145.00");
  const [result, setResult] = useState<{ risk_score: number; is_fraud: boolean; model_name: string } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true); setError(""); setResult(null);
    try {
      const values = features.split(",").map((value) => Number(value.trim()));
      if (mode === "credit-card" && (values.length !== 28 || values.some(Number.isNaN))) throw new Error("Enter exactly 28 numeric feature values.");
      const endpoint = mode === "credit-card" ? "/api/v1/fraud/credit-card/predict" : "/api/v1/fraud/paysim/predict";
      const body = mode === "credit-card" ? { time: 0, features: values, amount: Number(amount) } : { step: 1, amount: Number(amount), old_balance_org: 1000, new_balance_orig: 1000 - Number(amount), old_balance_dest: 0, new_balance_dest: Number(amount), is_flagged_fraud: 0 };
      setResult(await apiFetch<{ risk_score: number; is_fraud: boolean; model_name: string }>(endpoint, {
        method: "POST",
        body: JSON.stringify(body),
      }));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to complete the score.");
    } finally {
      setLoading(false);
    }
  }

  return <div className="dashboard-page">
    <section className="page-heading"><div><span className="eyebrow">Risk operations</span><h1>Fraud detection</h1><p>Score a transaction against the trained baseline and keep an eye on new signals.</p></div><Badge tone="green">Models online</Badge></section>
    <section className="fraud-layout">
      <article className="panel scoring-panel"><div className="panel-heading"><div><span className="eyebrow">Live scoring</span><h2>Check a transaction</h2></div><ShieldCheck size={22} className="panel-icon" /></div>
        <div className="mode-tabs"><button className={mode === "credit-card" ? "mode-active" : ""} onClick={() => setMode("credit-card")}>Credit card</button><button className={mode === "paysim" ? "mode-active" : ""} onClick={() => setMode("paysim")}>PaySim</button></div>
        <form onSubmit={handleSubmit} className="score-form"><label>Amount<input value={amount} onChange={(event) => setAmount(event.target.value)} type="number" min="0" step="0.01" /></label>{mode === "credit-card" && <label>V1-V28 feature vector<textarea value={features} onChange={(event) => setFeatures(event.target.value)} rows={5} /></label>}<button className="primary-button" disabled={loading}>{loading ? <LoaderCircle className="spin" size={17} /> : <ShieldCheck size={17} />}{loading ? "Scoring transaction" : "Run fraud score"}</button></form>
        {error && <div className="form-alert"><AlertTriangle size={16} />{error}</div>}
      </article>
      <article className={`panel result-panel ${result ? "has-result" : ""}`}><span className="eyebrow">Latest result</span>{result ? <><div className={`result-orb ${result.is_fraud ? "result-danger" : "result-safe"}`}>{result.is_fraud ? <AlertTriangle size={30} /> : <CheckCircle2 size={30} />}</div><h2>{result.is_fraud ? "Review recommended" : "Looks within range"}</h2><div className="risk-score"><strong>{Math.round(result.risk_score * 100)}%</strong><span>risk score</span></div><p>Scored by {result.model_name.replaceAll("_", " ")}</p><button className="text-link">Open investigation <ArrowUpRight size={14} /></button></> : <div className="empty-result"><ShieldCheck size={34} /><strong>Ready when you are</strong><span>Submit a transaction to see its risk score and model response.</span></div>}</article>
    </section>
  </div>;
}
