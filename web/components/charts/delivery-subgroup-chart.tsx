"use client";

import { useMemo, useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { DeliverySatisfactionContract, DeliverySubgroupEffect, DeliverySubgroupType } from "@/lib/contracts";
import { formatInteger, labelCategory } from "@/lib/format";

type PlotRow = DeliverySubgroupEffect & { label: string; differencePct: number };

function effectLabel(type: DeliverySubgroupType, value: string) {
  if (type === "category") return labelCategory(value);
  return value;
}

function SubgroupTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload: PlotRow }> }) {
  const row = payload?.[0]?.payload;
  if (!active || !row) return null;
  return <div className="chart-tooltip">
    <strong>{row.label}</strong>
    <span>+{row.differencePct.toFixed(2)} pp raw difference</span>
    <small>Late {(row.lateRisk * 100).toFixed(2)}% · n={formatInteger.format(row.lateReviewed)}</small>
    <small>On-time/early {(row.onTimeRisk * 100).toFixed(2)}% · n={formatInteger.format(row.onTimeReviewed)}</small>
  </div>;
}

export function DeliverySubgroupChart({ subgroupEffects, heterogeneity }: Pick<DeliverySatisfactionContract, "subgroupEffects" | "heterogeneity">) {
  const [type, setType] = useState<DeliverySubgroupType>("state");
  const selectedHeterogeneity = heterogeneity.find((row) => row.type === type)!;
  const plot = useMemo(() => {
    const sorted = subgroupEffects.filter((row) => row.type === type).sort((a, b) => b.riskDifference - a.riskDifference);
    const extremes = sorted.length <= 12 ? sorted : [...sorted.slice(0, 6), ...sorted.slice(-6)];
    return extremes.map((row): PlotRow => ({ ...row, label: effectLabel(type, row.group), differencePct: row.riskDifference * 100 }));
  }, [subgroupEffects, type]);
  return <>
    <div className="chart-control-row subgroup-control-row">
      <span>Raw low-review risk differences · high and low extremes</span>
      <div className="segmented-control" aria-label="Subgroup dimension">
        {(["month", "state", "category"] as const).map((value) => <button key={value} type="button" aria-pressed={type === value} onClick={() => setType(value)}>{value[0].toUpperCase() + value.slice(1)}</button>)}
      </div>
    </div>
    <div className="chart-wrap subgroup-chart" role="img" aria-label={`Exploratory ${type} subgroup raw risk differences. Only groups with at least 20 reviewed late and 20 reviewed on-time or early orders are included.`}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={plot} layout="vertical" margin={{ top: 2, right: 16, bottom: 2, left: 2 }}>
          <CartesianGrid horizontal={false} stroke="var(--chart-grid)" />
          <XAxis type="number" domain={[0, 70]} ticks={[0, 20, 40, 60]} axisLine={false} tickLine={false} tick={{ fill: "var(--ink-muted)", fontSize: 11 }} tickFormatter={(value: number) => `${value} pp`} />
          <YAxis type="category" dataKey="label" width={126} axisLine={false} tickLine={false} tick={{ fill: "var(--ink-muted)", fontSize: 10 }} />
          <Tooltip content={<SubgroupTooltip />} cursor={{ fill: "var(--surface-muted)" }} />
          <Bar dataKey="differencePct" fill="var(--accent)" radius={[0, 3, 3, 0]} maxBarSize={14} />
        </BarChart>
      </ResponsiveContainer>
    </div>
    <p className="heterogeneity-note"><strong>I² {(selectedHeterogeneity.iSquared * 100).toFixed(1)}%</strong> across {selectedHeterogeneity.includedGroups} eligible {type} groups · Q({selectedHeterogeneity.degreesFreedom})={selectedHeterogeneity.q.toFixed(2)} · exploratory, unadjusted and not multiplicity-corrected.</p>
  </>;
}
