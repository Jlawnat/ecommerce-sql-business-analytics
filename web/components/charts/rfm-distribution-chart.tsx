"use client";

import { useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { RfmSegment } from "@/lib/contracts";
import { formatInteger } from "@/lib/format";

const SHORT: Record<string, string> = {
  "Inactive in observed window": "Inactive",
  "High-value one-time customers": "High-value one-time",
  "Recent one-time customers": "Recent one-time",
  "Other established one-time customers": "Other established",
  "Champions": "Champions",
  "Repeat customers at risk": "Repeat at risk",
  "Loyal repeat customers": "Loyal repeat",
};

type RfmMode = "customers" | "value";

function RfmTooltip({ active, payload, mode }: { active?: boolean; payload?: Array<{ payload: RfmSegment }>; mode: RfmMode }) {
  const row = payload?.[0]?.payload;
  if (!active || !row) return null;
  return <div className="chart-tooltip"><strong>{row.segment}</strong><span>{mode === "customers" ? `${formatInteger.format(row.customers)} customers` : `${row.merchandiseSharePct.toFixed(2)}% of merchandise value`}</span><small>{row.customerSharePct.toFixed(2)}% of observed customers</small><small>{row.merchandiseSharePct.toFixed(2)}% of merchandise value</small></div>;
}

export function RfmDistributionChart({ data }: { data: RfmSegment[] }) {
  const [mode, setMode] = useState<RfmMode>("customers");
  const dataKey = mode === "customers" ? "customerSharePct" : "merchandiseSharePct";
  return <>
    <div className="rfm-toolbar">
      <span>{mode === "customers" ? "Share of observed customers" : "Share of merchandise value"}</span>
      <div className="segmented-control" aria-label="RFM comparison measure">
        <button type="button" aria-pressed={mode === "customers"} onClick={() => setMode("customers")}>Customers</button>
        <button type="button" aria-pressed={mode === "value"} onClick={() => setMode("value")}>Merchandise value</button>
      </div>
    </div>
    <div className="chart-wrap rfm-chart" role="img" aria-label={`Distribution of ${mode === "customers" ? "observed customers" : "merchandise value"} across seven RFM segments at the 2018-09-01 snapshot.`}>
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} layout="vertical" margin={{ top: 8, right: 12, bottom: 0, left: 10 }}>
        <CartesianGrid horizontal={false} stroke="var(--chart-grid)" />
        <XAxis type="number" axisLine={false} tickLine={false} tick={{ fill: "var(--ink-muted)", fontSize: 11 }} tickFormatter={(value: number) => `${value}%`} />
        <YAxis type="category" dataKey="segment" width={116} axisLine={false} tickLine={false} tick={{ fill: "var(--ink-muted)", fontSize: 11 }} tickFormatter={(value: string) => SHORT[value] ?? value} />
        <Tooltip content={<RfmTooltip mode={mode} />} cursor={{ fill: "var(--surface-muted)" }} />
        <Bar dataKey={dataKey} fill="var(--accent)" radius={[0, 3, 3, 0]} maxBarSize={20} />
      </BarChart>
    </ResponsiveContainer>
    </div>
    <p className="rfm-definition"><strong>Snapshot:</strong> purchases before 2018-09-01. “Inactive” means no recent purchase inside the observed window; it is not confirmed churn.</p>
  </>;
}
