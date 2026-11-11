# GitHub Actions CI Failure Remediation Implementation Plan

> **Execution record:** Implement directly on `feature/dashboard-v2`; do not commit, push, merge, deploy, or rewrite history.

**Goal:** Make the repository-overhaul CI reproducible on Python 3.11 and ensure the genuine Methodology screenshot is included by the next reviewed commit.

**Architecture:** Preserve the documented Python 3.11 support floor and resolve the full dependency graph inside an isolated Python 3.11 interpreter. Keep README screenshot links unchanged when they already target the genuine local capture, and strengthen repository tests so the lock remains compatible with the CI interpreter.

**Tech Stack:** Python 3.11, pip, unittest, GitHub Actions, Next.js 16, Markdown.

**Spec:** User request “Fix GitHub Actions CI failures”, remote commit `bb95373`, 2026-11-11.

## Global Constraints

- Work only on `feature/dashboard-v2` without rewriting Git history.
- Do not generate a fake screenshot or weaken CI checks.
- Do not change the research engine, Streamlit application, published aggregates, or statistical results.
- Do not commit, push, merge, or deploy.

## Review Focus

- The Methodology screenshot must be the genuine existing PNG and every link must use its exact filename.
- The lock must be resolved and installed by Python 3.11, not inferred from the current Python 3.14 environment.
- All transitive packages, not only NumPy, must satisfy Python 3.11 metadata.
- Clean-CI tests must remain distinct from licensed real-data audits.
- No generated dependency/build directory may become tracked.

---

### Task 1: Screenshot inclusion and link integrity

**Files:**
- Include: `visualizations/screenshots/v2/methodology-1024-showcase.png`
- Verify: `README.md`
- Verify: `docs/portfolio/README.md`

- [x] Confirm the local PNG is genuine, valid, correctly sized, and not ignored.
- [x] Confirm both Markdown documents use the same exact filename.
- [x] Stage the genuine asset for inclusion in the next user-reviewed commit and add a repository-checker regression test for untracked README screenshots.

### Task 2: Python 3.11 dependency lock

**Files:**
- Modify: `requirements.lock`
- Test: `tests/test_repository_hygiene.py`

- [x] Resolve direct dependencies from `requirements.txt` in an isolated Python 3.11 environment.
- [x] Replace the lock with the complete compatible resolution.
- [x] Inspect every installed distribution's `Requires-Python` metadata against Python 3.11.18.
- [x] Install the finished lock into a second clean Python 3.11 environment and run `pip check`.

### Task 3: End-to-end validation

**Files:**
- Modify only Task 1–2 files if validation exposes a defect.

- [x] Run repository hygiene, Markdown, screenshot, privacy, and workflow checks.
- [x] Run the clean-CI Python/SQL suite and applicable full local tests.
- [x] Run frontend data contracts, TypeScript, ESLint, and production build.
- [x] Verify Git state, tracked artifacts, and unchanged published research/Streamlit modules.
