type BadgeTone = "green" | "amber" | "red" | "slate";

export function Badge({ children, tone = "slate" }: { children: React.ReactNode; tone?: BadgeTone }) {
  return <span className={`badge badge-${tone}`}><i />{children}</span>;
}
