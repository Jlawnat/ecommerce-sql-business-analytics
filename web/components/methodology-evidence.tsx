"use client";

import { useMemo, useState } from "react";
import { ArrowRight, ArrowUpRight, CheckCircle2, Code2, FileCode2, Search } from "lucide-react";
import { DataStatus, PageHeader, ResearchCaveat } from "@/components/analytics-primitives";
import {
  evidenceResources,
  metricDefinitions,
  metricFamilies,
  pipelineStages,
  qualityEvidence,
  reproductionCommands,
  statisticalMethods,
  validationLayers,
  type EvidenceLink,
  type MetricFamily,
} from "@/lib/methodology-content";

const REPOSITORY = "https://github.com/Jlawnat/ecommerce-sql-business-analytics";
const SOURCE_ROOT = `${REPOSITORY}/blob/feature/dashboard-v2`;

function EvidenceAnchor({ source }: { source: EvidenceLink }) {
  return <a className="method-source" href={`${SOURCE_ROOT}/${source.path}`} target="_blank" rel="noreferrer">
    <span>{source.label}</span><small>{source.kind}</small><ArrowUpRight aria-hidden="true" size={13} />
  </a>;
}

function PipelineExplorer() {
  const [selectedId, setSelectedId] = useState(pipelineStages[0].id);
  const selected = pipelineStages.find((stage) => stage.id === selectedId) ?? pipelineStages[0];

  return <section className="method-section pipeline-section" aria-labelledby="pipeline-title">
    <div className="method-section-heading">
      <div><h2 id="pipeline-title">Research pipeline</h2><p>Follow one claim from licensed source files to an aggregate decision surface.</p></div>
      <span>Seven controlled transitions</span>
    </div>
    <div className="pipeline-track" role="group" aria-label="Research pipeline stages">
      {pipelineStages.map((stage, index) => <button
        type="button"
        key={stage.id}
        className={selected.id === stage.id ? "is-selected" : ""}
        aria-pressed={selected.id === stage.id}
        onClick={() => setSelectedId(stage.id)}
      ><span>{stage.title}</span>{index < pipelineStages.length - 1 && <ArrowRight aria-hidden="true" size={13} />}</button>)}
    </div>
    <div className="pipeline-detail" aria-live="polite">
      <div className="pipeline-narrative">
        <h3>{selected.title}</h3>
        <p>{selected.summary}</p>
        <div><strong>Binding grain</strong><p>{selected.grain}</p></div>
      </div>
      <div className="pipeline-checks">
        <strong>Controls</strong>
        <ul>{selected.checks.map((check) => <li key={check}><CheckCircle2 aria-hidden="true" size={14} />{check}</li>)}</ul>
      </div>
      <div className="pipeline-outputs">
        <strong>Produces</strong>
        <ul>{selected.outputs.map((output) => <li key={output}>{output}</li>)}</ul>
        <div className="source-cluster">{selected.sources.map((source) => <EvidenceAnchor key={source.path} source={source} />)}</div>
      </div>
    </div>
  </section>;
}

function MetricDictionary() {
  const [family, setFamily] = useState<"All" | MetricFamily>("All");
  const [query, setQuery] = useState("");
  const [selectedId, setSelectedId] = useState(metricDefinitions[0].id);
  const filtered = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return metricDefinitions.filter((metric) => {
      const matchesFamily = family === "All" || metric.family === family;
      const searchable = `${metric.name} ${metric.definition} ${metric.population} ${metric.unit}`.toLowerCase();
      return matchesFamily && (!normalized || searchable.includes(normalized));
    });
  }, [family, query]);
  const selected = filtered.find((metric) => metric.id === selectedId) ?? filtered[0];

  return <section className="method-section dictionary-section" aria-labelledby="dictionary-title">
    <div className="method-section-heading">
      <div><h2 id="dictionary-title">Interactive metric dictionary</h2><p>Definitions remain identical to the research layer; this interface only makes their populations and exclusions easier to inspect.</p></div>
      <span>{filtered.length} of {metricDefinitions.length} definitions</span>
    </div>
    <div className="dictionary-tools">
      <label className="metric-search"><Search aria-hidden="true" size={15} /><span className="sr-only">Search metric definitions</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search definitions or populations" /></label>
      <div className="method-filter" role="group" aria-label="Filter metrics by research area">
        {metricFamilies.map((option) => <button type="button" key={option} aria-pressed={family === option} onClick={() => setFamily(option)}>{option}</button>)}
      </div>
    </div>
    {selected ? <div className="dictionary-workspace">
      <div className="metric-index" role="listbox" aria-label="Metric definitions">
        {filtered.map((metric) => <button
          type="button"
          role="option"
          aria-selected={selected.id === metric.id}
          className={selected.id === metric.id ? "is-selected" : ""}
          key={metric.id}
          onClick={() => setSelectedId(metric.id)}
        ><span>{metric.name}</span><small>{metric.family} · {metric.unit}</small></button>)}
      </div>
      <article className="metric-definition-detail" aria-live="polite">
        <header><span>{selected.family}</span><h3>{selected.name}</h3><p>{selected.definition}</p></header>
        <dl>
          <div><dt>Unit</dt><dd>{selected.unit}</dd></div>
          <div><dt>Population</dt><dd>{selected.population}</dd></div>
          <div><dt>Denominator</dt><dd>{selected.denominator}</dd></div>
          <div><dt>Observation window</dt><dd>{selected.window}</dd></div>
          <div><dt>Exclusions</dt><dd>{selected.exclusions}</dd></div>
          <div><dt>Missingness and interpretation</dt><dd>{selected.missingness}</dd></div>
        </dl>
        <div className="source-cluster">{selected.sources.map((source) => <EvidenceAnchor key={source.path} source={source} />)}</div>
      </article>
    </div> : <div className="method-empty" role="status">No metric definition matches this search. Change the phrase or select another research area.</div>}
  </section>;
}

function StatisticalExplorer() {
  const [selectedId, setSelectedId] = useState(statisticalMethods[0].id);
  const selected = statisticalMethods.find((method) => method.id === selectedId) ?? statisticalMethods[0];
  return <section className="method-section statistical-section" aria-labelledby="statistical-title">
    <div className="method-section-heading">
      <div><h2 id="statistical-title">Statistical methods explorer</h2><p>Start with the business reading, then open implementation, diagnostics and limits only when needed.</p></div>
      <span>Documented estimators · no frontend refitting</span>
    </div>
    <div className="statistical-workspace">
      <div className="method-index" role="tablist" aria-label="Statistical methods">
        {statisticalMethods.map((method) => <button
          key={method.id}
          type="button"
          role="tab"
          aria-selected={method.id === selected.id}
          onClick={() => setSelectedId(method.id)}
        >{method.title}</button>)}
      </div>
      <article className="method-detail" role="tabpanel" aria-live="polite">
        <h3>{selected.title}</h3>
        <p className="method-business-reading"><strong>Business reading.</strong> {selected.businessReading}</p>
        <div className="estimand"><strong>What is estimated</strong><p>{selected.estimand}</p></div>
        <div className="method-disclosures">
          <details open><summary>Implementation</summary><ul>{selected.implementation.map((item) => <li key={item}>{item}</li>)}</ul></details>
          <details><summary>Diagnostics and robustness</summary><ul>{selected.diagnostics.map((item) => <li key={item}>{item}</li>)}</ul></details>
          <details><summary>Interpretation limits</summary><ul>{selected.limitations.map((item) => <li key={item}>{item}</li>)}</ul></details>
        </div>
        <div className="source-cluster">{selected.sources.map((source) => <EvidenceAnchor key={source.path} source={source} />)}</div>
      </article>
    </div>
  </section>;
}

function QualityValidation() {
  return <section className="method-section quality-section" aria-labelledby="quality-title">
    <div className="method-section-heading">
      <div><h2 id="quality-title">Data quality and validation</h2><p>Quality flags remain visible; prevention and reconciliation happen before presentation.</p></div>
      <span>Phase 1 findings · Phase 2.5 assertions</span>
    </div>
    <div className="quality-strip">
      {qualityEvidence.map((item) => <div key={item.label} className={`quality-item is-${item.tone}`}><span>{item.label}</span><strong className="num">{item.value}</strong><small>{item.note}</small></div>)}
    </div>
    <div className="validation-list">
      {validationLayers.map((layer) => <article key={layer.title}><div><h3>{layer.title}</h3><p>{layer.detail}</p></div><EvidenceAnchor source={layer.source} /></article>)}
    </div>
    <div className="fanout-note"><strong>Join fan-out rule</strong><p>Never join unaggregated items, payments and reviews before aggregating money. Each child domain is reduced to the analysis grain first; the measured naive join would add <span className="num">5,657</span> rows above item grain.</p><EvidenceAnchor source={{ label: "Read the quality framework", path: "docs/DATA_QUALITY.md", kind: "documentation" }} /></div>
  </section>;
}

function ReproducibilityEvidence() {
  return <section className="method-section reproducibility-section" aria-labelledby="repro-title">
    <div className="method-section-heading">
      <div><h2 id="repro-title">Reproducibility and evidence</h2><p>Rebuild locally from licensed source files, inspect the evidence, and publish only allowlisted aggregates.</p></div>
      <a className="repository-action" href={REPOSITORY} target="_blank" rel="noreferrer"><Code2 aria-hidden="true" size={15} />Open GitHub repository<ArrowUpRight aria-hidden="true" size={13} /></a>
    </div>
    <div className="repro-grid">
      <div className="evidence-directory">
        {evidenceResources.map((resource) => <article key={resource.group}><h3>{resource.group}</h3><p>{resource.description}</p><div className="source-cluster">{resource.links.map((source) => <EvidenceAnchor key={source.path} source={source} />)}</div></article>)}
      </div>
      <div className="reproduction-panel">
        <div><FileCode2 aria-hidden="true" size={17} /><h3>Reproduction sequence</h3></div>
        <ol>{reproductionCommands.map((command) => <li key={command}><code>{command}</code></li>)}</ol>
        <p>Raw files must be acquired manually from Kaggle. Tests that require the licensed local database skip only when that database is unavailable.</p>
      </div>
    </div>
    <div className="policy-grid">
      <details open><summary>Source attribution and licensing</summary><p>The Brazilian E-Commerce Public Dataset by Olist covers anonymized marketplace activity from 2016–2018 and is licensed CC BY-NC-SA 4.0. Attribution, non-commercial use and compatible share-alike terms apply. The dataset is not redistributed by this repository.</p><EvidenceAnchor source={{ label: "Attribution and acquisition", path: "docs/DATA_SOURCE.md", kind: "documentation" }} /></details>
      <details><summary>Download and privacy policy</summary><p>Dashboard downloads are aggregate-only. Raw source files, local databases, mart rows, customer snapshots and model-population rows are outside the export allowlist. No customer-level drill-through is provided.</p><EvidenceAnchor source={{ label: "Presentation and export contract", path: "docs/PHASE3_DATA_CONTRACTS.md", kind: "documentation" }} /></details>
      <details><summary>Observational research limits</summary><p>Historical associations do not establish causal effects. Acquisition, off-platform behavior, carrier and route factors, marketing exposure, costs and randomized assignment are unavailable; adjustment and robustness checks cannot recover those missing designs or variables.</p><EvidenceAnchor source={{ label: "Independent research audit", path: "docs/PHASE25_AUDIT.md", kind: "documentation" }} /></details>
    </div>
  </section>;
}

export function MethodologyEvidence() {
  return <div className="overview-page methodology-page">
    <PageHeader
      title="Methodology & evidence"
      description="Trace definitions, analytical grain, uncertainty and validation from the Olist source through every published dashboard claim."
      actions={<DataStatus observationEnd="August 2018" />}
    />
    <section className="methodology-intro" aria-labelledby="methodology-question">
      <div><h2 id="methodology-question">Can every decision be traced back to a controlled definition?</h2><p>This explorer connects four dashboard views to their source population, SQL grain, statistical method, automated checks and publication boundary.</p></div>
      <dl>
        <div><dt>Source tables</dt><dd className="num">9</dd></div>
        <div><dt>Mart assertions</dt><dd className="num">12</dd></div>
        <div><dt>Aggregate contracts</dt><dd className="num">3</dd></div>
        <div><dt>Research views</dt><dd className="num">4</dd></div>
      </dl>
    </section>
    <nav className="methodology-local-nav" aria-label="Methodology page sections">
      <a href="#pipeline-title">Pipeline</a><a href="#dictionary-title">Metrics</a><a href="#statistical-title">Methods</a><a href="#quality-title">Validation</a><a href="#repro-title">Evidence</a>
    </nav>
    <PipelineExplorer />
    <MetricDictionary />
    <StatisticalExplorer />
    <QualityValidation />
    <ReproducibilityEvidence />
    <ResearchCaveat summary="Scientific boundary · reproducible evidence is not causal identification">
      <p>The project preserves observed populations, uncertainty and missingness, but cannot observe true acquisition, off-platform orders, all operational confounders or randomized treatment assignment. Statistical adjustment supports a more comparable historical association; it does not turn that association into an intervention effect.</p>
      <a href={`${SOURCE_ROOT}/docs/PHASE25_AUDIT.md`} target="_blank" rel="noreferrer">Read the independent audit <ArrowUpRight aria-hidden="true" size={14} /></a>
    </ResearchCaveat>
  </div>;
}
