import { Badge } from "../ui/Badge";
export function AlertCard({ title, description }: { title: string; description: string }) { return <div className="signal-item"><div><strong>{title}</strong><span>{description}</span></div><Badge tone="amber">Review</Badge></div>; }
