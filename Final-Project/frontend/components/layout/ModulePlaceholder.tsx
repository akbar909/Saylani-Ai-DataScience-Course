import Link from "next/link";
import { ArrowRight, Bot, CreditCard, FileText, Plug, ScrollText, Settings } from "lucide-react";

const icons = { Bot, FileText, ScrollText, Plug, CreditCard, Settings };

export function ModulePlaceholder({ icon, eyebrow, title, description, action = "Back to overview" }: { icon: keyof typeof icons; eyebrow: string; title: string; description: string; action?: string }) {
  const Icon = icons[icon];
  return <div className="dashboard-page"><section className="page-heading"><div><span className="eyebrow">{eyebrow}</span><h1>{title}</h1><p>{description}</p></div></section><article className="panel empty-module"><Icon size={28} /><h2>Workspace connection is ready</h2><p>This view is part of the product surface. Its data connection and actions will be enabled as the corresponding backend module is completed.</p><Link href="/dashboard" className="outline-button">{action} <ArrowRight size={15} /></Link></article></div>;
}
