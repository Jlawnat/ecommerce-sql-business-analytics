"use client";

import { ArrowRight, CheckCircle2, FlaskConical, Route } from "lucide-react";
import type { DeliveryModelSummary, DeliverySatisfactionContract } from "@/lib/contracts";
import { formatInteger } from "@/lib/format";
import { ChartPanel, DataStatus, ExportAction, InsightHero, MetricCard, PageHeader, ResearchCaveat, SourceLink } from "@/components/analytics-primitives";
import { DeliveryComparisonChart } from "@/components/charts/delivery-comparison-chart";
import { DeliverySubgroupChart } from "@/components/charts/delivery-subgroup-chart";

const REPO = "https://github.com/Jlawnat/ecommerce-sql-business-analytics/blob/main";
const pct = (value: number) => `${(value * 100).toFixed(2)}%`;
const pp = (value: number) => `${value >= 0 ? "+" : ""}${(value * 100).toFixed(2)} pp`;

function RiskContrast({ data }: { data: DeliverySatisfactionContract["observedContrast"] }) {
  return <div className="delivery-risk-contrast">
    <p>Observed low-review rate</p>
    <div className="risk-row is-late"><span>Late</span><i><b style={{ width: `${data.lateRisk * 100}%` }} /></i><strong className="num">{pct(data.lateRisk)}</strong></div>
    <div className="risk-row"><span>On-time / early</span><i><b style={{ width: `${data.onTimeRisk * 100}%` }} /></i><strong className="num">{pct(data.onTimeRisk)}</strong></div>
    <small>Raw difference <strong className="num">{pp(data.riskDifference)}</strong> · observational</small>
  </div>;
}

function ModelRow({ model }: { model: DeliveryModelSummary }) {
  return <div className="model-row">
    <div><strong>{model.label}</strong><span>{formatInteger.format(model.reviewedOrders)} reviewed orders · {model.outcome.replaceAll("_", " ")}</span></div>
    <div><span>Adjusted OR</span><strong className="num">{model.oddsRatio.toFixed(2)}</strong><small className="num">95% CI {model.orCi95Low.toFixed(2)}–{model.orCi95High.toFixed(2)}</small></div>
    <div><span>Standardized difference</span><strong className="num">{pp(model.riskDifference)}</strong><small className="num">95% CI {pp(model.rdCi95Low)} to {pp(model.rdCi95High)}</small></div>
  </div>;
}

function MissingReviewSensitivity({ data }: { data: DeliverySatisfactionContract["missingReviewBounds"] }) {
  const floor = 0.40;
  const ceiling = 0.48;
  const position = (value: number) => `${((value - floor) / (ceiling - floor)) * 100}%`;
  return <div className="missing-sensitivity">
    <div className="sensitivity-scale" aria-label={`Worst-case raw risk-difference bounds ${pp(data.worstCaseMinimum)} to ${pp(data.worstCaseMaximum)}. Observed ${pp(data.observedRiskDifference)}.`}>
      <span style={{ left: position(data.worstCaseMinimum) }} />
      <i style={{ left: position(data.worstCaseMinimum), right: `${100 - Number.parseFloat(position(data.worstCaseMaximum))}%` }} />
      <span style={{ left: position(data.worstCaseMaximum) }} />
      <b style={{ left: position(data.observedRiskDifference) }} />
    </div>
    <div className="sensitivity-labels"><span>{pp(data.worstCaseMinimum)} minimum</span><strong>{pp(data.observedRiskDifference)} observed</strong><span>{pp(data.worstCaseMaximum)} maximum</span></div>
    <p>Extreme assignments for all <strong className="num">{formatInteger.format(data.lateMissingReviews)}</strong> late and <strong className="num">{formatInteger.format(data.onTimeMissingReviews)}</strong> on-time/early missing reviews leave the raw association large.</p>
  </div>;
}

export function DeliverySatisfaction({ data }: { data: DeliverySatisfactionContract }) {
  function exportComparisons() {
    const headers = ["dimension", "group", "eligible_orders", "late_orders", "late_rate", "ci95_low", "ci95_high", "average_review_score"];
    const rows = [
      ...data.comparisons.states.map((row) => ["state", row.group, row.eligibleOrders, row.lateOrders, row.lateRate, row.ci95Low, row.ci95High, row.averageReviewScore]),
      ...data.comparisons.categories.map((row) => ["category", row.group, row.eligibleOrders, row.lateOrders, row.lateRate, row.ci95Low, row.ci95High, row.averageReviewScore]),
    ];
    const blob = new Blob([[headers.join(","), ...rows.map((row) => row.join(","))].join("\n") + "\n"], { type: "text/csv;charset=utf-8" });
    const href = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = href;
    anchor.download = "olist-delivery-comparisons-aggregate.csv";
    anchor.click();
    URL.revokeObjectURL(href);
  }

  return <div className="overview-page delivery-page">
    <PageHeader
      title="Delivery & satisfaction"
      description="Observed delivery timing, low-review risk, adjusted associations and operational evidence boundaries."
      actions={<><DataStatus observationEnd={data.dataset.observationEnd} /><ExportAction onClick={exportComparisons} label="Export comparisons" /></>}
    />

    <InsightHero
      eyebrow="Primary delivery finding"
      title={<>Late orders show a <span className="num">53.99%</span> low-review rate.</>}
      body={<>On-time or early orders show <strong className="num">9.19%</strong>. Measured adjustment leaves a strong association, but the historical observational design cannot identify a causal delivery effect.</>}
    ><RiskContrast data={data.observedContrast} /></InsightHero>

    <section className="metric-strip delivery-metrics" aria-label="Delivery research headline metrics">
      <MetricCard label="Late low-review rate" value={pct(data.observedContrast.lateRisk)} note={`95% CI ${pct(data.observedContrast.lateCi95Low)}–${pct(data.observedContrast.lateCi95High)}`} />
      <MetricCard label="On-time / early rate" value={pct(data.observedContrast.onTimeRisk)} note={`95% CI ${pct(data.observedContrast.onTimeCi95Low)}–${pct(data.observedContrast.onTimeCi95High)}`} />
      <MetricCard label="Adjusted odds ratio" value={data.primaryModel.oddsRatio.toFixed(2)} note={`95% CI ${data.primaryModel.orCi95Low.toFixed(2)}–${data.primaryModel.orCi95High.toFixed(2)}`} />
      <MetricCard label="Standardized risk difference" value={pp(data.primaryModel.riskDifference)} note={`95% CI ${pp(data.primaryModel.rdCi95Low)} to ${pp(data.primaryModel.rdCi95High)}`} lead />
    </section>

    <ChartPanel
      title="Where is late-delivery exposure highest?"
      question={`Compare adequately sized states and attributed categories; groups require at least ${formatInteger.format(data.comparisons.minimumEligibleOrders)} timing-eligible orders.`}
      meta="Late rate · 95% Wilson CI"
      className="delivery-comparison-panel"
      footer={<div className="panel-footer"><span>Descriptive comparisons may reflect geography, seller mix, item characteristics and other confounding.</span><SourceLink href={`${REPO}/${data.lineage.stateSource}`}>Comparison aggregates</SourceLink></div>}
    ><DeliveryComparisonChart data={data.comparisons} /></ChartPanel>

    <section className="model-evidence" aria-labelledby="model-title">
      <div className="model-heading">
        <div><p className="context-label">Adjusted evidence</p><h2 id="model-title">The association remains large across prespecified sensitivity checks.</h2></div>
        <SourceLink href={`${REPO}/${data.lineage.modelSource}`}>Model results</SourceLink>
      </div>
      <ModelRow model={data.primaryModel} />
      {data.sensitivities.map((model) => <ModelRow key={model.key} model={model} />)}
      <p className="model-definition">Grouped-binomial logistic regression adjusts for purchase period, customer state, category group, merchandise-value band and single- versus multi-seller status. Odds ratios are conditional and non-collapsible; standardized risks remain model-dependent.</p>
    </section>

    <div className="delivery-research-grid">
      <ChartPanel
        title="Subgroup heterogeneity"
        question="How widely does the raw late-versus-on-time low-review contrast vary across eligible subgroups?"
        meta="Exploratory raw differences"
        footer={<SourceLink href={`${REPO}/${data.lineage.researchSummary}`}>Heterogeneity methods</SourceLink>}
      ><DeliverySubgroupChart subgroupEffects={data.subgroupEffects} heterogeneity={data.heterogeneity} /></ChartPanel>

      <section className="diagnostic-stack" aria-labelledby="diagnostics-title">
        <div className="diagnostic-heading"><p className="context-label">Model diagnostics</p><h2 id="diagnostics-title">Discrimination is moderate; calibration error is non-zero.</h2></div>
        <div className="diagnostic-strip">
          <div><span>AUC</span><strong className="num">{data.primaryModel.auc.toFixed(3)}</strong><small>Ranking discrimination</small></div>
          <div><span>Brier score</span><strong className="num">{data.primaryModel.brierScore.toFixed(4)}</strong><small>Mean probability error</small></div>
          <div><span>Parameters</span><strong className="num">{data.primaryModel.parameters}</strong><small>{data.primaryModel.iterations} iterations</small></div>
          <div><span>Fit status</span><strong>{data.primaryModel.converged ? "Converged" : "Not converged"}</strong><small>{formatInteger.format(data.primaryModel.events)} low reviews</small></div>
        </div>
        <p className="diagnostic-limit">AUC and Brier score describe this fitted historical model. They do not establish causal identification, transportability, or intervention performance. Carrier, route distance and promise-construction fields are unavailable.</p>
        <div className="missing-review-block"><h3>Missing-review sensitivity</h3><MissingReviewSensitivity data={data.missingReviewBounds} /></div>
      </section>
    </div>

    <section className="recommendation-section" aria-labelledby="recommendations-title">
      <div className="recommendation-heading"><p className="context-label">Evidence-linked next actions</p><h2 id="recommendations-title">Use the association to prioritize measurement and prospective validation.</h2></div>
      <div className="recommendation-grid">
        <article><FlaskConical aria-hidden="true" size={19} /><h3>Test service recovery</h3><p>Instrument a real-time late-order flag and standardized outreach while preserving a randomized no-contact control group.</p><small>Measure low-review share and mean score under intention to treat; guard review completion, contact rate, complaints, credits and latency.</small><a href={`${REPO}/${data.lineage.researchSummary}`} target="_blank" rel="noreferrer">Evidence and validation design <ArrowRight size={13} /></a></article>
        <article><Route aria-hidden="true" size={19} /><h3>Diagnose lanes and sellers</h3><p>Start with adequately sized MA, CE, BA and RJ exposure, then decompose by carrier, seller and origin–destination lane before changing routing.</p><small>Current state/category differences are exploratory and confounded; collect p90 delay and promise-construction fields.</small><a href={`${REPO}/${data.lineage.phase2Summary}`} target="_blank" rel="noreferrer">State and category evidence <ArrowRight size={13} /></a></article>
        <article><CheckCircle2 aria-hidden="true" size={19} /><h3>Keep evidence gates</h3><p>Publish denominators, uncertainty, review coverage and prespecified subgroup thresholds with each operational monitor.</p><small>Do not turn historical ORs or risk differences into promised uplift. Re-estimate prospectively after instrumentation changes.</small><a href={`${REPO}/${data.lineage.researchSql}`} target="_blank" rel="noreferrer">Research SQL <ArrowRight size={13} /></a></article>
      </div>
    </section>

    <ResearchCaveat summary="Observational boundary · association is not a causal effect">
      <p>Timing and review outcomes are measured at order level after averaging multiple review rows. Adjustment covers observed purchase period, state, category, value band and seller count, but residual confounding, review selection, dependence across customers or sellers, and unavailable carrier/route factors remain. Subgroup analyses are exploratory and are not multiplicity-adjusted.</p>
      <a href={`${REPO}/${data.lineage.researchSummary}`} target="_blank" rel="noreferrer">Read complete statistical research summary <ArrowRight aria-hidden="true" size={14} /></a>
    </ResearchCaveat>
  </div>;
}
