"use client";

import { CartesianGrid, ComposedChart, ErrorBar, ResponsiveContainer, Scatter, Tooltip, XAxis, YAxis } from "recharts";
import type { RepeatEstimate } from "@/lib/contracts";
import { formatInteger } from "@/lib/format";

type PlotRow = RepeatEstimate & { estimatePct: number; ciError: [number, number] };

function RepeatTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload: PlotRow }> }) {
  const row = payload?.[0]?.payload;
  if (!active || !row) return null;
  return <div className="chart-tooltip"><strong>Day {row.horizonDays}</strong><span>{row.estimatePct.toFixed(2)}% repeated</span><small>95% CI {(row.ci95Low * 100).toFixed(2)}–{(row.ci95High * 100).toFixed(2)}%</small><small>{formatInteger.format(row.riskSet)} in risk set</small></div>;
}

export function RepeatIncidenceChart({ data }: { data: RepeatEstimate[] }) {
  const plot: PlotRow[] = data.map((row) => ({
    ...row,
    estimatePct: row.repeatIncidence * 100,
    ciError: [(row.repeatIncidence - row.ci95Low) * 100, (row.ci95High - row.repeatIncidence) * 100],
  }));
  return <div className="chart-wrap customer-chart" role="img" aria-label="Selected-horizon Kaplan-Meier cumulative incidence estimates at 30, 60, 90, 180 and 365 days. Points are not connected and vertical marks show 95 percent confidence intervals.">
    <ResponsiveContainer width="100%" height="100%">
      <ComposedChart data={plot} margin={{ top: 12, right: 12, bottom: 2, left: 0 }}>
        <CartesianGrid vertical={false} stroke="var(--chart-grid)" />
        <XAxis dataKey="horizonDays" axisLine={false} tickLine={false} tick={{ fill: "var(--ink-muted)", fontSize: 12 }} tickFormatter={(value: number) => `${value}d`} />
        <YAxis domain={[0, 4.5]} axisLine={false} tickLine={false} width={42} tick={{ fill: "var(--ink-muted)", fontSize: 12 }} tickFormatter={(value: number) => `${value}%`} />
        <Tooltip content={<RepeatTooltip />} cursor={{ stroke: "var(--control)" }} />
        <Scatter data={plot} dataKey="estimatePct" fill="var(--accent)" shape="circle">
          <ErrorBar dataKey="ciError" direction="y" width={7} stroke="var(--accent-dark)" strokeWidth={1.5} />
        </Scatter>
      </ComposedChart>
    </ResponsiveContainer>
  </div>;
}
