"use client";

import { CartesianGrid, Line, LineChart, ReferenceDot, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { MonthlyAggregate } from "@/lib/contracts";
import { formatCompactMoney, formatInteger, formatMoney } from "@/lib/format";

const statusLabel: Record<MonthlyAggregate["observationStatus"], string> = {
  complete_or_well_represented: "Complete or well represented",
  incomplete_first_month: "Incomplete first month",
  incomplete_last_month: "Incomplete last month",
  sparse_month: "Sparse month",
};

function TrendTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload: MonthlyAggregate }> }) {
  const row = payload?.[0]?.payload;
  if (!active || !row) return null;
  return (
    <div className="chart-tooltip">
      <strong>{row.month}</strong>
      <span>{formatMoney.format(row.merchandiseValue)}</span>
      <small>{formatInteger.format(row.deliveredOrders)} delivered orders</small>
      {row.observationStatus !== "complete_or_well_represented" && <em>{statusLabel[row.observationStatus]}</em>}
    </div>
  );
}

export function SalesTrendChart({ data }: { data: MonthlyAggregate[] }) {
  const exceptions = data.filter((row) => row.observationStatus !== "complete_or_well_represented");
  return (
    <div className="chart-wrap" role="img" aria-label={`Monthly delivered merchandise value from ${data[0]?.month} through ${data.at(-1)?.month}. Sparse and incomplete boundary months are marked in amber.`}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 14, right: 12, bottom: 2, left: 2 }}>
          <CartesianGrid vertical={false} stroke="var(--chart-grid)" strokeWidth={1} />
          <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: "var(--ink-muted)", fontSize: 12 }} minTickGap={34} tickFormatter={(value: string) => value.slice(2)} />
          <YAxis axisLine={false} tickLine={false} width={58} tick={{ fill: "var(--ink-muted)", fontSize: 12 }} tickFormatter={(value: number) => formatCompactMoney.format(value).replace("BRL", "").trim()} />
          <Tooltip content={<TrendTooltip />} cursor={{ stroke: "var(--control)", strokeWidth: 1 }} />
          <Line type="linear" dataKey="merchandiseValue" stroke="var(--accent)" strokeWidth={2.5} dot={false} activeDot={{ r: 4, fill: "var(--sheet)", stroke: "var(--accent)", strokeWidth: 2 }} />
          {exceptions.map((row) => <ReferenceDot key={row.month} x={row.month} y={row.merchandiseValue} r={4} fill="var(--warning)" stroke="var(--sheet)" strokeWidth={1.5} />)}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
