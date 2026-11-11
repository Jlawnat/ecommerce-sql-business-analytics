"use client";

import { useMemo, useState } from "react";
import type { CohortCell } from "@/lib/contracts";

export function CohortHeatmap({ data }: { data: CohortCell[] }) {
  const [horizon, setHorizon] = useState(12);
  const verifiedOutlier = data.find((row) => row.cohortMonth === "2016-12" && row.monthNumber === 1) ?? null;
  const [selected, setSelected] = useState<CohortCell | null>(verifiedOutlier);
  const months = useMemo(() => [...new Set(data.map((row) => row.cohortMonth))], [data]);
  const lookup = useMemo(() => new Map(data.map((row) => [`${row.cohortMonth}:${row.monthNumber}`, row])), [data]);
  const maturity = useMemo(() => new Map(months.map((cohort) => [
    cohort,
    Math.max(...data.filter((row) => row.cohortMonth === cohort && row.observed).map((row) => row.monthNumber)),
  ])), [data, months]);
  const columns = Array.from({ length: horizon + 1 }, (_, index) => index);
  return <>
    <div className="heatmap-toolbar"><span>Months since first order</span><div className="segmented-control" aria-label="Heatmap horizon">
      {[6, 12, 18].map((value) => <button key={value} type="button" aria-pressed={horizon === value} onClick={() => setHorizon(value)}>{value} mo</button>)}
    </div></div>
    <div className="heatmap-scroll" tabIndex={0} aria-label="Cohort retention heatmap. Month zero is 100 percent by construction; unavailable censored cells are shown with dashes.">
      <div className="heatmap-grid" style={{ gridTemplateColumns: `84px repeat(${columns.length}, 44px)` }}>
        <span className="heatmap-corner">Cohort</span>
        {columns.map((month) => <span className="heatmap-axis" key={month}>M{month}</span>)}
        {months.map((cohort) => <div className="heatmap-row" key={cohort} style={{ gridColumn: `1 / span ${columns.length + 1}`, gridTemplateColumns: `84px repeat(${columns.length}, 44px)` }}>
          <span className="heatmap-label">{cohort}</span>
          {columns.map((month) => {
            const cell = lookup.get(`${cohort}:${month}`);
            const unavailable = !cell?.observed;
            const rate = cell?.retentionRatePct ?? null;
            const alpha = month === 0 ? 1 : Math.min(0.95, 0.16 + (rate ?? 0) / 1.6);
            if (unavailable) return <span
              key={month}
              className="heatmap-cell is-censored"
              title={`${cohort}, month ${month}: unavailable because the cohort has not matured to this horizon`}
            >—</span>;
            return <button
              key={month}
              type="button"
              className={`heatmap-cell${month === 0 ? " is-baseline" : ""}${selected === cell ? " is-selected" : ""}`}
              style={month > 0 ? { backgroundColor: `rgba(11,107,105,${alpha})` } : undefined}
              onClick={() => setSelected(cell ?? null)}
              aria-label={`${cohort}, month ${month}: ${rate?.toFixed(2)} percent, ${cell?.retainedCustomers} of ${cell?.acquiredCustomers} customers retained, observed through month ${maturity.get(cohort)}`}
            >{month === 0 ? "100" : rate?.toFixed(1)}</button>;
          })}
        </div>)}
      </div>
    </div>
    {selected && <div className={`cohort-cell-detail${selected.acquiredCustomers < 30 ? " is-small-sample" : ""}`} aria-live="polite">
      <div><span>Selected cell</span><strong className="num">{selected.cohortMonth} · M{selected.monthNumber} · {selected.retentionRatePct?.toFixed(2)}%</strong></div>
      <div><span>Cohort size</span><strong className="num">{selected.acquiredCustomers}</strong></div>
      <div><span>Retained</span><strong className="num">{selected.retainedCustomers}</strong></div>
      <div><span>Observation maturity</span><strong className="num">Through M{maturity.get(selected.cohortMonth)}</strong></div>
      {selected.acquiredCustomers < 30 && <p><strong>Small sample:</strong> this percentage is unstable. The 2016-12 M1 value is verified as 1 of 1 customer, not a population-level pattern.</p>}
    </div>}
    <div className="heatmap-legend"><span><i className="baseline-swatch" /> Month 0 · fixed baseline</span><span><i className="scale-swatch" /> Later-month retention</span><span><i className="censored-swatch" /> Unavailable / censored</span></div>
  </>;
}
