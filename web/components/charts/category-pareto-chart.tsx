"use client";

import { useEffect, useState } from "react";
import { Bar, CartesianGrid, ComposedChart, Line, ReferenceDot, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { CategoryAggregate } from "@/lib/contracts";
import { formatCompactMoney, formatMoney, labelCategory } from "@/lib/format";

function shortCategory(value: string) {
  const labels: Record<string, string> = {
    health_beauty: "Health & beauty", watches_gifts: "Watches", bed_bath_table: "Bed & bath",
    sports_leisure: "Sports", computers_accessories: "Computers", furniture_decor: "Décor",
    computers: "Computers*", pet_shop: "Pet shop", musical_instruments: "Music", small_appliances: "Appliances",
  };
  return labels[value] ?? labelCategory(value).split(" ")[0];
}

function ParetoTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload: CategoryAggregate }> }) {
  const row = payload?.[0]?.payload;
  if (!active || !row) return null;
  return <div className="chart-tooltip"><strong>#{row.rank} · {labelCategory(row.category)}</strong><span>{formatMoney.format(row.merchandiseValue)}</span><small>{row.sharePct.toFixed(2)}% category share · {row.cumulativeSharePct.toFixed(2)}% cumulative</small></div>;
}

export function CategoryParetoChart({ data }: { data: CategoryAggregate[] }) {
  const [compact, setCompact] = useState(false);
  const threshold = data.find((row) => row.rank === 18);
  const rankByCategory = new Map(data.map((row) => [row.category, row.rank]));
  useEffect(() => {
    const media = window.matchMedia("(max-width: 520px)");
    const update = () => setCompact(media.matches);
    update();
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, []);
  const tickLabel = (category: string) => {
    const rank = rankByCategory.get(category);
    if (!compact) return shortCategory(category);
    if (rank === 1) return "Health";
    if (rank === 10 || rank === 18) return shortCategory(category);
    return "";
  };
  return (
    <div className="chart-wrap pareto-chart" role="img" aria-label="Top 20 categories ranked by delivered merchandise value, with cumulative share reaching 81.29% at category 18.">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 14, right: 2, bottom: 22, left: 2 }}>
          <CartesianGrid vertical={false} stroke="var(--chart-grid)" />
          <XAxis dataKey="category" interval={compact ? 0 : 1} angle={0} axisLine={false} tickLine={false} height={42} tick={{ fill: "var(--ink-muted)", fontSize: compact ? 9 : 11 }} tickFormatter={tickLabel} />
          <YAxis yAxisId="value" axisLine={false} tickLine={false} width={58} tick={{ fill: "var(--ink-muted)", fontSize: 11 }} tickFormatter={(value: number) => formatCompactMoney.format(value).replace("BRL", "").trim()} />
          <YAxis yAxisId="share" orientation="right" domain={[0, 100]} ticks={[0, 40, 80, 100]} axisLine={false} tickLine={false} width={34} tick={{ fill: "var(--ink-muted)", fontSize: 11 }} tickFormatter={(value: number) => `${value}%`} />
          <Tooltip content={<ParetoTooltip />} cursor={{ fill: "var(--active)" }} />
          <ReferenceLine yAxisId="share" y={80} stroke="var(--warning)" strokeDasharray="4 4" label={{ value: "80%", position: "insideTopRight", fill: "var(--warning)", fontSize: 11 }} />
          {threshold && <ReferenceLine yAxisId="share" x={threshold.category} stroke="var(--warning)" strokeDasharray="2 3" label={{ value: "18 categories · 81.29%", position: "insideTopRight", fill: "var(--warning)", fontSize: 11 }} />}
          <Bar yAxisId="value" dataKey="merchandiseValue" fill="var(--accent-soft)" stroke="var(--accent)" strokeWidth={0.5} radius={[2, 2, 0, 0]} maxBarSize={28} />
          <Line yAxisId="share" type="linear" dataKey="cumulativeSharePct" stroke="var(--ink)" strokeWidth={1.8} dot={false} activeDot={{ r: 3, fill: "var(--sheet)", stroke: "var(--ink)", strokeWidth: 2 }} />
          {threshold && <ReferenceDot yAxisId="share" x={threshold.category} y={threshold.cumulativeSharePct} r={5} fill="var(--warning)" stroke="var(--sheet)" strokeWidth={2} />}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
