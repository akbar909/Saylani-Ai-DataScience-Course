"use client";

import Link from "next/link";
import { ArrowUpRight, ShieldCheck } from "lucide-react";

import { KPICard } from "../../../components/charts/KPICard";
import { Badge } from "../../../components/ui/Badge";
import { Skeleton } from "../../../components/ui/Skeleton";
import { useOverview } from "../../../hooks/useOverview";
import { formatPercent } from "../../../lib/utils";

export default function DashboardPage() {
  const { data, error, loading } = useOverview();
  const credit = data?.models.creditcard;
  const paysim = data?.models.paysim;
  return (
    <div className="dashboard-page">
      <section className="page-heading">
        <div><span className="eyebrow">Connected workspace</span><h1>Finance command center.</h1><p>Every metric below comes from the backend or is clearly marked unavailable.</p></div>
        <Link href="/reports" className="outline-button">View reports <ArrowUpRight size={15} /></Link>
      </section>

      {error && <div className="form-alert">Backend overview unavailable: {error}</div>}
      <section className="kpi-grid">
        {loading ? [1, 2, 3, 4].map((item) => <Skeleton className="kpi-card" key={item} />) : <>
          <KPICard label="Credit-card recall" value={formatPercent(credit?.recall)} change="model metric" detail="stratified holdout" trend="up" />
          <KPICard label="Credit-card PR-AUC" value={formatPercent(credit?.pr_auc)} change="model metric" detail="precision-recall area" trend="up" />
          <KPICard label="PaySim recall" value={formatPercent(paysim?.recall)} change="model metric" detail="time-aware holdout" trend="up" />
          <KPICard label="PaySim PR-AUC" value={formatPercent(paysim?.pr_auc)} change="model metric" detail="precision-recall area" trend="up" />
        </>}
      </section>

      <section className="dashboard-grid">
        <article className="panel cash-panel"><div className="panel-heading"><div><span className="eyebrow">Artifact health</span><h2>Model performance</h2></div><Badge tone="green">Backend sourced</Badge></div><div className="model-health-grid"><div><strong>Credit card</strong><span>ROC-AUC {formatPercent(credit?.roc_auc)}</span></div><div><strong>PaySim</strong><span>ROC-AUC {formatPercent(paysim?.roc_auc)}</span></div></div><p className="data-note">These are evaluation metrics from saved training artifacts, not synthetic financial activity.</p></article>
        <article className="panel signal-panel"><div className="panel-heading"><div><span className="eyebrow">Live ingestion</span><h2>Signals</h2></div><ShieldCheck size={21} className="panel-icon" /></div>{data?.signals.length ? data.signals.map((signal, index) => <div className="signal-item" key={index}><strong>{signal.title}</strong><span>{signal.description}</span></div>) : <div className="empty-result compact"><ShieldCheck size={28} /><strong>No signals ingested</strong><span>Connect Mongo-backed transactions to populate this feed.</span></div>}</article>
      </section>

      <section className="panel transactions-panel">
        <div className="panel-heading"><div><span className="eyebrow">Latest activity</span><h2>Recent transactions</h2></div><Link href="/fraud-detection" className="text-link">Open monitor <ArrowUpRight size={14} /></Link></div>
        {data?.transactions.length ? <div className="transaction-table">{data.transactions.map((transaction, index) => <div className="table-row" key={index}>{Object.values(transaction).map((value, cellIndex) => <span key={cellIndex}>{value}</span>)}</div>)}</div> : <div className="empty-table"><strong>No transactions available yet.</strong><span>The API returned an empty transaction feed. Import a CSV or connect an integration before this table is populated.</span></div>}
      </section>
    </div>
  );
}
