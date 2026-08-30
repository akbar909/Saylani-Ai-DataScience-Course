export function Card({ children, className="" }: { children: React.ReactNode; className?: string }) { return <article className={`panel ${className}`}>{children}</article>; }
