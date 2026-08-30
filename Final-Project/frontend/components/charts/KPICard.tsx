import { ArrowDownRight, ArrowUpRight, Minus } from "lucide-react";

type Trend = "up" | "down" | "flat";

export function KPICard({ label, value, change, trend = "up", detail }: { label: string; value: string; change: string; trend?: Trend; detail: string }) {
  const TrendIcon = trend === "up" ? ArrowUpRight : trend === "down" ? ArrowDownRight : Minus;
  return (
    <article className="kpi-card">
      <div className="kpi-heading"><span>{label}</span><span className={`trend trend-${trend}`}><TrendIcon size={14} />{change}</span></div>
      <strong className="kpi-value">{value}</strong>
      <span className="kpi-detail">{detail}</span>
      <div className={`kpi-spark spark-${trend}`}><span /><span /><span /><span /><span /><span /><span /></div>
    </article>
  );
}
