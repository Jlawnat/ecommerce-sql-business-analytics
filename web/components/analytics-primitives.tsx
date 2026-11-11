import type { ReactNode } from "react";
import { AlertTriangle, ArrowUpRight, CheckCircle2, Database, Download, Info } from "lucide-react";
import { cn } from "@/lib/cn";

export function PageHeader({ title, description, actions }: { title: string; description: string; actions?: ReactNode }) {
  return (
    <header className="page-header">
      <div><h1>{title}</h1><p>{description}</p></div>
      {actions && <div className="page-actions">{actions}</div>}
    </header>
  );
}

export function DataStatus({ observationEnd }: { observationEnd: string }) {
  return <span className="data-status"><CheckCircle2 aria-hidden="true" size={14} /> Verified snapshot · through {observationEnd}</span>;
}

export function InsightHero({ eyebrow, title, body, children }: { eyebrow: string; title: ReactNode; body: ReactNode; children: ReactNode }) {
  return (
    <section className="insight-hero" aria-labelledby="primary-finding">
      <div className="insight-copy"><p className="context-label">{eyebrow}</p><h2 id="primary-finding">{title}</h2><p>{body}</p></div>
      <div className="signature-evidence">{children}</div>
    </section>
  );
}

export function MetricCard({ label, value, exactValue, note, lead = false }: { label: string; value: string; exactValue?: string; note: string; lead?: boolean }) {
  return (
    <article className={cn("metric-card", lead && "metric-lead")} aria-label={`${label}: ${exactValue ?? value}. ${note}`}>
      <p>{label}</p><strong className="num" title={exactValue}>{value}</strong><small>{note}</small>
    </article>
  );
}

export function EvidenceCard({ title, children, href, linkLabel = "Open evidence" }: { title: string; children: ReactNode; href: string; linkLabel?: string }) {
  return (
    <article className="evidence-card">
      <div><h3>{title}</h3><p>{children}</p><a href={href} target="_blank" rel="noreferrer">{linkLabel}<ArrowUpRight aria-hidden="true" size={14} /></a></div>
    </article>
  );
}

export function ChartPanel({ title, question, meta, children, footer, className }: { title: string; question: string; meta: string; children: ReactNode; footer?: ReactNode; className?: string }) {
  return (
    <section className={cn("chart-panel", className)}>
      <header><div><h2>{title}</h2><p>{question}</p></div><span>{meta}</span></header>
      {children}
      {footer && <footer>{footer}</footer>}
    </section>
  );
}

export function ConfidenceIntervalDisplay({ estimate, low, high, label }: { estimate: string; low: string; high: string; label: string }) {
  return <div className="ci-display" aria-label={`${label}: ${estimate}, 95% confidence interval ${low} to ${high}`}><strong>{estimate}</strong><span><i style={{ left: low }} /><b style={{ left: high }} /><em style={{ left: estimate }} /></span><small>{label} · 95% CI {low}–{high}</small></div>;
}

export function ResearchCaveat({ summary, children }: { summary: string; children: ReactNode }) {
  return <details className="research-caveat"><summary><AlertTriangle aria-hidden="true" size={16} /><span>{summary}</span><span className="caveat-more">Read boundary</span></summary><div>{children}</div></details>;
}

export function SourceLink({ href, children }: { href: string; children: ReactNode }) {
  return <a className="source-link" href={href} target="_blank" rel="noreferrer"><Database aria-hidden="true" size={14} />{children}<ArrowUpRight aria-hidden="true" size={13} /></a>;
}

export function ExportAction({ onClick, label = "Export aggregate" }: { onClick: () => void; label?: string }) {
  return <button className="export-action" type="button" onClick={onClick}><Download aria-hidden="true" size={15} />{label}</button>;
}

export function EmptyState({ children }: { children: ReactNode }) {
  return <div className="empty-state"><Info aria-hidden="true" size={16} />{children}</div>;
}
