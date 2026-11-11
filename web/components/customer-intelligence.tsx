"use client";

import { ArrowRight, ShieldCheck } from "lucide-react";
import type { CustomerIntelligenceContract } from "@/lib/contracts";
import { formatInteger } from "@/lib/format";
import { ChartPanel, DataStatus, ExportAction, InsightHero, MetricCard, PageHeader, ResearchCaveat, SourceLink } from "@/components/analytics-primitives";
import { CohortHeatmap } from "@/components/cohort-heatmap";
import { RepeatIncidenceChart } from "@/components/charts/repeat-incidence-chart";
import { RfmDistributionChart } from "@/components/charts/rfm-distribution-chart";

const REPO = "https://github.com/Jlawnat/ecommerce-sql-business-analytics/blob/main";
const pct = (value: number) => `${(value * 100).toFixed(2)}%`;

function RepeatMilestones({ data }: { data: CustomerIntelligenceContract }) {
  return <div className="repeat-milestones">
    <p>Observed cumulative incidence</p>
    <div><span><small>Day 90</small><strong className="num">{pct(data.summary.repeat90.repeatIncidence)}</strong><em>95% CI {pct(data.summary.repeat90.ci95Low)}–{pct(data.summary.repeat90.ci95High)}</em></span><ArrowRight aria-hidden="true" size={18} /><span><small>Day 365</small><strong className="num">{pct(data.summary.repeat365.repeatIncidence)}</strong><em>95% CI {pct(data.summary.repeat365.ci95Low)}–{pct(data.summary.repeat365.ci95High)}</em></span></div>
  </div>;
}

export function CustomerIntelligence({ data }: { data: CustomerIntelligenceContract }) {
  function exportCohorts() {
    const headers = ["cohort_month", "month_number", "acquired_customers", "is_observed", "retained_customers", "retention_rate_pct"];
    const rows = data.cohorts.map((row) => [row.cohortMonth, row.monthNumber, row.acquiredCustomers, row.observed ? 1 : 0, row.retainedCustomers ?? "", row.retentionRatePct ?? ""].join(","));
    const blob = new Blob([[headers.join(","), ...rows].join("\n") + "\n"], { type: "text/csv;charset=utf-8" });
    const href = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = href;
    anchor.download = "olist-cohort-retention-aggregate.csv";
    anchor.click();
    URL.revokeObjectURL(href);
  }

  return <div className="overview-page customer-page">
    <PageHeader
      title="Customer intelligence"
      description="Repeat-purchase incidence, mature cohort retention and aggregate customer value segments."
      actions={<><DataStatus observationEnd={data.dataset.observationEnd} /><ExportAction onClick={exportCohorts} label="Export cohorts" /></>}
    />

    <InsightHero
      eyebrow="Primary customer finding"
      title={<>Observed repeat reaches <span className="num">3.81%</span> by day 365.</>}
      body={<>Repeat purchase is uncommon in the observed window. Kaplan–Meier estimation accounts for right censoring, but this remains a historical descriptive result—not a churn diagnosis or causal claim.</>}
    ><RepeatMilestones data={data} /></InsightHero>

    <section className="metric-strip customer-metrics" aria-label="Customer research headline metrics">
      <MetricCard label="Observed customers" value={formatInteger.format(data.summary.observedCustomers)} note="Unique customer population" />
      <MetricCard label="Repeat by day 90" value={pct(data.summary.repeat90.repeatIncidence)} note={`95% CI ${pct(data.summary.repeat90.ci95Low)}–${pct(data.summary.repeat90.ci95High)}`} />
      <MetricCard label="Repeat by day 365" value={pct(data.summary.repeat365.repeatIncidence)} note={`95% CI ${pct(data.summary.repeat365.ci95Low)}–${pct(data.summary.repeat365.ci95High)}`} lead />
      <MetricCard label="RFM exact agreement" value={`${(data.summary.stability.exactAgreement * 100).toFixed(1)}%`} note={`κ ${data.summary.stability.cohenKappa.toFixed(3)} · two snapshots`} />
    </section>

    <ChartPanel
      title="Cohort retention"
      question="Among acquired customers, what share returns in each observable later month?"
      meta="Customer cohorts · percentage"
      className="cohort-panel"
      footer={<div className="panel-footer"><span>Month 0 is neutral because 100% is true by construction; later cells use their own meaningful teal scale.</span><SourceLink href={`${REPO}/${data.lineage.cohortSource}`}>Cohort aggregate</SourceLink></div>}
    ><CohortHeatmap data={data.cohorts} /></ChartPanel>

    <div className="customer-grid">
      <ChartPanel title="Repeat incidence" question="What is the observed second-purchase incidence at the five verified follow-up horizons?" meta="Selected-horizon KM estimates · 95% CI" footer={<div className="panel-footer"><span>Discrete points only; no intermediate event-time estimates are implied.</span><SourceLink href={`${REPO}/${data.lineage.kmSource}`}>KM aggregate</SourceLink></div>}>
        <RepeatIncidenceChart data={data.km} />
      </ChartPanel>
      <ChartPanel title="RFM segmentation" question="How do segment shares differ when viewed by customers versus merchandise value?" meta="Snapshot · 2018-09-01" footer={<SourceLink href={`${REPO}/${data.lineage.rfmSource}`}>RFM aggregate</SourceLink>}>
        <RfmDistributionChart data={data.rfm} />
      </ChartPanel>
    </div>

    <section className="stability-panel" aria-labelledby="stability-title">
      <div><p className="context-label">Snapshot stability</p><h2 id="stability-title">Segment labels are moderately stable—not permanent identities.</h2><p>Across <strong className="num">{formatInteger.format(data.summary.stability.commonCustomers)}</strong> customers shared by the June and September 2018 snapshots, exact segment agreement is <strong className="num">{(data.summary.stability.exactAgreement * 100).toFixed(1)}%</strong> and Cohen’s κ is <strong className="num">{data.summary.stability.cohenKappa.toFixed(3)}</strong>.</p></div>
      <div className="stability-mark"><ShieldCheck aria-hidden="true" size={20} /><span><small>Comparison</small><strong>Jun → Sep 2018</strong></span></div>
    </section>

    <ResearchCaveat summary="Censoring boundary · unavailable cells are not zero retention">
      <p>Later cohorts have not had enough observation time to reach every horizon. Those cells remain unavailable. Kaplan–Meier estimates describe observed repeat incidence under right censoring; they do not prove customer churn or identify an intervention effect.</p>
      <a href={`${REPO}/${data.lineage.researchSummary}`} target="_blank" rel="noreferrer">Read statistical research summary <ArrowRight aria-hidden="true" size={14} /></a>
    </ResearchCaveat>
  </div>;
}
