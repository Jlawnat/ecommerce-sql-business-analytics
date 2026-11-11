# Repository audit

Audit date: 2026-11-11. Scope: research architecture, documentation, dashboards, dependencies, tests, CI readiness, licensing, privacy, and presentation.

## Priority findings

| Priority | Finding | Resolution in this overhaul |
|---|---|---|
| High | Root README described Streamlit as the portfolio endpoint and did not present Dashboard V2 | Rebuilt as a V2-first research portfolio landing page with genuine screenshots and case studies |
| High | No GitHub Actions workflow existed | Added clean-checkout documentation/privacy, Python/SQL, contract, TypeScript, ESLint, and build jobs |
| High | Clean CI and licensed real-data audits were not separated | Excluded the four database-dependent audit tests from clean CI and documented the local command |
| High | Repository had no explicit code license | Documented dataset/code separation; author still needs to select a code license before claiming open-source licensing |
| Medium | Documentation was authoritative but flat | Added audience indexes under architecture, research, engineering, and portfolio without moving source documents |
| Medium | Python application dependencies used broad ranges | Pinned direct Streamlit, pandas, and Plotly versions; frontend already had a complete lockfile |
| Medium | No automated Markdown, Mermaid, screenshot, or privacy gate | Added a dependency-free checker with unit tests and CI execution |
| Low | `.gitignore` repeated the Next.js section | Consolidated rules and added common Node/Python build artifacts |

## Architecture strengths preserved

- Nine-file manifest and normalized source schema.
- Idempotent, failure-atomic ingestion.
- Explicit source/mart grains and measured join fan-out risk.
- Standard-library SQL/statistical pipeline with checked-in evidence.
- Independent real-data anchors and synthetic known-answer tests.
- Strict aggregate presentation contracts and export allowlist.
- Separate, preserved Streamlit and premium Next.js applications.

## Remaining release risks

1. **Code license decision:** the dataset license is documented, but no license currently grants reuse of the project code.
2. **Next.js deployment:** no public V2 origin has been deployed and verified; README correctly provides local launch instructions only.
3. **Clean CI cannot reproduce licensed-data audits:** expected by design; maintainers must run the documented local gate before publishing changed research outputs.
4. **Python transitive dependencies:** direct application packages are pinned, but the repository does not maintain a platform-specific fully resolved Python lockfile.

## Metric claim audit

The portfolio uses exact verified anchors from [`reports/PHASE1_RESULTS.md`](../../reports/PHASE1_RESULTS.md) and [`reports/PHASE25_RESEARCH_RESULTS.md`](../../reports/PHASE25_RESEARCH_RESULTS.md). Nine source tables contain 1,550,922 rows in total, which is approximately 1.55 million; the proposed 1.45 million approximation was rejected as inconsistent with the published table counts.
