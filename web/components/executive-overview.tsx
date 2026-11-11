"use client";

import { useMemo, useState } from "react";
import { ArrowDown, ArrowRight } from "lucide-react";
import type { ExecutiveOverviewContract } from "@/lib/contracts";
import { formatCompactMoney, formatInteger, formatMoney, labelCategory } from "@/lib/format";
import { CategoryParetoChart } from "@/components/charts/category-pareto-chart";
import { SalesTrendChart } from "@/components/charts/sales-trend-chart";
import { FilterToolbar, type SalesWindow } from "@/components/filter-toolbar";
import { ChartPanel, DataStatus, EvidenceCard, ExportAction, InsightHero, MetricCard, PageHeader, ResearchCaveat, SourceLink } from "@/components/analytics-primitives";

const REPO = "https://github.com/Jlawnat/ecommerce-sql-business-analytics/blob/main";

function ParetoStaircase({ data, threshold }: { data: ExecutiveOverviewContract["categories"]; threshold: number }) {
  const first80 = data.filter((row) => row.inFirst80Pct);
  const max = first80[0]?.merchandiseValue ?? 1;
  return (
    <div className="pareto-staircase" aria-label={`${threshold} categories are required to exceed 80 percent of delivered merchandise value`}>
      <div className="staircase-head"><span>Category concentration</span><strong className="num">80%</strong></div>
      <div className="staircase-bars" aria-hidden="true">
        {first80.map((row) => <i key={row.category} style={{ height: `${Math.max(16, row.merchandiseValue / max * 100)}%` }} />)}
      </div>
      <div className="staircase-foot"><span><b className="num">1</b> {labelCategory(first80[0]?.category ?? "")}</span><ArrowRight aria-hidden="true" size={15} /><span><b className="num">{threshold}</b> categories</span></div>
    </div>
  );
}

export function ExecutiveOverview({ data }: { data: ExecutiveOverviewContract }) {
  const [window, setWindow] = useState<SalesWindow>("all");
  const monthly = useMemo(() => data.monthly.filter((row) => window === "all" || row.month.startsWith(window)), [data.monthly, window]);
  const selected = useMemo(() => {
    const deliveredOrders = monthly.reduce((total, row) => total + row.deliveredOrders, 0);
    const cents = monthly.reduce((total, row) => total + Math.round(row.merchandiseValue * 100), 0);
    const merchandiseValue = cents / 100;
    return { deliveredOrders, merchandiseValue, averageOrderValue: Math.round((merchandiseValue / deliveredOrders) * 100) / 100 };
  }, [monthly]);

  function exportAggregate() {
    const headers = ["purchase_month", "delivered_orders", "merchandise_value", "avg_merchandise_value_per_order", "observation_status"];
    const lines = monthly.map((row) => [row.month, row.deliveredOrders, row.merchandiseValue.toFixed(2), row.averageOrderValue.toFixed(2), row.observationStatus].join(","));
    const blob = new Blob([[headers.join(","), ...lines].join("\n") + "\n"], { type: "text/csv;charset=utf-8" });
    const href = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = href;
    anchor.download = `olist-monthly-sales-${window}.csv`;
    anchor.click();
    URL.revokeObjectURL(href);
  }

  const periodLabel = window === "all" ? "Full observed window" : window;
  return (
    <div className="overview-page">
      <PageHeader
        title="Executive overview"
        description="Delivered-order economics and category concentration in the historical Olist marketplace."
        actions={<><DataStatus observationEnd={data.dataset.observationEnd} /><ExportAction onClick={exportAggregate} label="Export CSV" /></>}
      />

      <InsightHero
        eyebrow="Primary business finding"
        title={<><span className="num">18 categories</span> carry 81.29% of value.</>}
        body={<>The portfolio is concentrated enough to require category discipline, but no single category dominates: <strong>{labelCategory(data.summary.topCategory)}</strong> contributes <strong className="num">{data.summary.topCategorySharePct.toFixed(2)}%</strong>.</>}
      >
        <ParetoStaircase data={data.categories} threshold={data.summary.categoriesToReach80Pct} />
      </InsightHero>

      <FilterToolbar value={window} onChange={setWindow} />

      <section className="metric-strip" aria-label={`${periodLabel} headline metrics`}>
        <MetricCard label="Delivered orders" value={formatInteger.format(selected.deliveredOrders)} note={`${periodLabel} · delivered only`} />
        <MetricCard label="Merchandise value" value={formatCompactMoney.format(selected.merchandiseValue)} exactValue={formatMoney.format(selected.merchandiseValue)} note="Excludes freight · not profit" lead />
        <MetricCard label="Average / order" value={formatMoney.format(selected.averageOrderValue)} note={`${periodLabel} · delivered orders`} />
        <MetricCard label="Largest category" value={`${data.summary.topCategorySharePct.toFixed(2)}%`} note={`${labelCategory(data.summary.topCategory)} · full window`} />
      </section>

      <div className="overview-grid">
        <ChartPanel
          title="Historical sales trajectory"
          question="How did delivered merchandise value move month by month?"
          meta={`BRL · ${monthly[0]?.month}–${monthly.at(-1)?.month}`}
          footer={<div className="panel-footer"><span className="annotation-key"><i /> Amber points are incomplete or sparse and excluded from interpreted growth claims.</span><SourceLink href={`${REPO}/${data.lineage.monthlySql}`}>Monthly SQL lineage</SourceLink></div>}
        >
          <SalesTrendChart data={monthly} />
        </ChartPanel>

        <aside className="decision-rail" aria-labelledby="priority-title">
          <div className="rail-heading"><h2 id="priority-title">Decision priorities</h2><span>Evidence-led next steps</span></div>
          <EvidenceCard title="Measure the second purchase" href={`${REPO}/reports/PHASE25_RESEARCH_RESULTS.md`}>
            Track 90- and 365-day repeat incidence with cohort maturity controls; one observed order is not proven churn.
          </EvidenceCard>
          <EvidenceCard title="Diagnose fulfilment" href={`${REPO}/sql/analysis/10_delivery_satisfaction_research.sql`}>
            Prioritise high-lateness state and category cells, then validate interventions prospectively.
          </EvidenceCard>
          <EvidenceCard title="Protect mix visibility" href={`${REPO}/sql/analysis/07_sales_category_trends.sql`}>
            Monitor the top 18 portfolio and documented month-mix shifts without interpreting sparse boundaries.
          </EvidenceCard>
        </aside>
      </div>

      <ChartPanel
        title="Category Pareto"
        question="How many categories account for most delivered merchandise value?"
        meta="Top 20 categories · full observed window"
        className="pareto-panel"
        footer={<div className="panel-footer"><span><strong className="num">18</strong> categories reach <strong className="num">81.29%</strong>; the leading category contributes <strong className="num">9.33%</strong>.</span><SourceLink href={`${REPO}/${data.lineage.categorySql}`}>Category SQL lineage</SourceLink></div>}
      >
        <CategoryParetoChart data={data.categories} />
      </ChartPanel>

      <ResearchCaveat summary="Historical evidence only · observation ends August 2018">
        <p>This snapshot does not describe current ecommerce conditions. September 2016 and August 2018 are incomplete, December 2016 is sparse, and no causal conclusions are drawn from observational associations.</p>
        <a href={`${REPO}/docs/METRIC_DEFINITIONS.md`} target="_blank" rel="noreferrer">Read KPI definitions <ArrowDown aria-hidden="true" size={14} /></a>
      </ResearchCaveat>
    </div>
  );
}
