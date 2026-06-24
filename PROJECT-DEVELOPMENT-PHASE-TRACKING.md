# PROJECT-DEVELOPMENT-PHASE-TRACKING.md — Energy/Carbon Footprint Optimizer (ESG)

Idea #83 · cluster `science-industry` · slug `energy-carbon-footprint-optimizer`

## Phase 0 — Research & Skill Architecture  ✅
- **Tasks:** survey domain frameworks; pick 7 named methodologies; define 6 scoring dimensions; choose crawl sources.
- **Deliverables:** framework list, dimension rubric, knowledge-source map.
- **Success criteria:** every dimension maps to ≥1 citable framework.
- **Effort:** 0.5 day.
- **Status:** DONE — frameworks catalogued in `src/energy_carbon_footprint_optimizer/constants.py` and `SECOND-KNOWLEDGE-BRAIN.md`.

## Phase 1 — Core Sub-Skills  ✅
- **Tasks:** implement 4 sub-skills: sub-evaluation-framework-selector, sub-scoring-engine, sub-improvement-roadmap, sub-compliance-check.
- **Deliverables:** `skills/sub-*.md`.
- **Success criteria:** each sub-skill has explicit inputs, outputs, tools, quality gate.
- **Effort:** 1 day.
- **Status:** DONE — all sub-skills reference the production implementation under `src/energy_carbon_footprint_optimizer/`.

## Phase 2 — Main Harness + Quality Gates  ✅
- **Tasks:** wire `skills/main.md`; encode compliance + standard quality gates; define output format.
- **Deliverables:** `skills/main.md`, Quality Gates checklist.
- **Success criteria:** harness refuses to emit output if any gate fails.
- **Effort:** 1 day.
- **Status:** DONE — `harness.py::run_harness` enforces intake, scoring, challenge, compliance and synthesis gates; raises `QualityGateError` / `ComplianceBlockedError` on failure.

## Phase 3 — SECOND-KNOWLEDGE-BRAIN Pipeline  ✅
- **Tasks:** finalize `tools/knowledge_updater.py` crawl4ai config; first seed crawl; dedup logic.
- **Deliverables:** populated Knowledge Update Log.
- **Success criteria:** ≥10 fresh, scored entries appended without duplicates.
- **Effort:** 1 day.
- **Status:** DONE — `python tools/knowledge_updater.py --seed` appended 12 scored, de-duplicated seed entries; dedup verified by `tests/test_knowledge_updater.py`.

## Phase 4 — Testing & Validation  ✅
- **Tasks:** run the 5 scenario tests in `tests/test-scenarios.md`; calibrate scoring.
- **Deliverables:** test results, calibration notes.
- **Success criteria:** all scenarios pass; scores reproducible within ±0.5.
- **Effort:** 1 day.
- **Status:** DONE — 14 pytest tests pass (5 scenarios + regression + knowledge updater); scoring is deterministic and reproducible.

## Phase 5 — Integration & Cross-Skill Wiring  ✅
- **Tasks:** share cluster sub-skills across `science-industry` siblings; standardize roadmap output.
- **Deliverables:** shared sub-skill references.
- **Success criteria:** no duplicated sub-skill logic within the cluster.
- **Effort:** 0.5 day.
- **Status:** DONE — `skills/shared-cluster-sub-skills.md`, `shared/science-industry/README.md` and `shared/science-industry/manifest.json` expose reusable modules and install instructions.

## Milestone Summary
| Phase | Status | Key output |
|-------|--------|-----------|
| 0 | ✅ | Architecture + frameworks |
| 1 | ✅ | 4 sub-skills |
| 2 | ✅ | Harness + gates |
| 3 | ✅ | Crawl pipeline + seeded knowledge log |
| 4 | ✅ | Test validation (14 passing) |
| 5 | ✅ | Cross-skill wiring |
