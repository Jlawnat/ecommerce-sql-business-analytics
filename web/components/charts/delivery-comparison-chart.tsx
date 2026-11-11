"use client";

import { useState } from "react";
import { Bar, BarChart, CartesianGrid, ErrorBar, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { DeliveryComparison, DeliverySatisfactionContract } from "@/lib/contracts";
import { formatInteger, labelCategory } from "@/lib/format";

type ComparisonMode = "states" | "categories";
type PlotRow = DeliveryComparison & { label: string; ratePct: number; ciError: [number, number] };

function ComparisonTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload: PlotRow }> }) {
  const row = payload?.[0]?.payload;
  if (!active || !row) return null;
  return <div className="chart-tooltip">
    <strong>{row.label}</strong>
    <span>{row.ratePct.toFixed(2)}% late</span>
    <small>95% Wilson CI {(row.ci95Low * 100).toFixed(2)}–{(row.ci95High * 100).toFixed(2)}%</small>
    <small>{formatInteger.format(row.lateOrders)} of {formatInteger.format(row.eligibleOrders)} eligible orders</small>
    <small>Average review {row.averageReviewScore.toFixed(2)} / 5</small>
  </div>;
}

export function DeliveryComparisonChart({ data }: { data: DeliverySatisfactionContract["comparisons"] }) {
  const [mode, setMode] = useState<ComparisonMode>("states");
  const source = mode === "states" ? data.states : data.categories;
  const selected = mode === "states"
    ? [...source.slice(0, 7), ...source.filter((row) => row.group === "SP")]
    : source.slice(0, 10);
  const plot: PlotRow[] = selected.map((row) => ({
    ...row,
    label: mode === "states" ? row.group : labelCategory(row.group),
    ratePct: row.lateRate * 100,
    ciError: [(row.lateRate - row.ci95Low) * 100, (row.ci95High - row.lateRate) * 100],
  }));
  return <>
    <div className="chart-control-row">
      <span>Highest late-delivery rates{mode === "states" ? " · SP included as volume benchmark" : ""}</span>
      <div className="segmented-control" aria-label="Delivery comparison dimension">
        <button type="button" aria-pressed={mode === "states"} onClick={() => setMode("states")}>States</button>
        <button type="button" aria-pressed={mode === "categories"} onClick={() => setMode("categories")}>Categories</button>
      </div>
    </div>
    <div className="chart-wrap delivery-comparison-chart" role="img" aria-label={`Late-delivery rates and 95 percent Wilson intervals for ${mode} with at least ${data.minimumEligibleOrders} timing-eligible orders.`}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={plot} layout="vertical" margin={{ top: 4, right: 22, bottom: 2, left: 2 }}>
          <CartesianGrid horizontal={false} stroke="var(--chart-grid)" />
          <XAxis type="number" domain={[0, 25]} ticks={[0, 5, 10, 15, 20, 25]} axisLine={false} tickLine={false} tick={{ fill: "var(--ink-muted)", fontSize: 11 }} tickFormatter={(value: number) => `${value}%`} />
          <YAxis type="category" dataKey="label" width={126} axisLine={false} tickLine={false} tick={{ fill: "var(--ink-muted)", fontSize: 11 }} />
          <Tooltip content={<ComparisonTooltip />} cursor={{ fill: "var(--surface-muted)" }} />
          <Bar dataKey="ratePct" fill="var(--accent)" radius={[0, 3, 3, 0]} maxBarSize={18}>
            <ErrorBar dataKey="ciError" direction="x" width={5} stroke="var(--ink)" strokeWidth={1.2} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  </>;
}
