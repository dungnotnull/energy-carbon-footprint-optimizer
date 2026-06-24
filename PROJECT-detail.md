# PROJECT-detail.md — Energy/Carbon Footprint Optimizer (ESG)

## Executive Summary
`energy-carbon-footprint-optimizer` is a Claude Skill in the **Science, Engineering & Industry** cluster (idea #83). It acts as a carbon-accounting and energy-efficiency analyst who quantifies and reduces footprints for individuals, households and SMEs. It runs a research-first, evidence-graded harness that profiles the input, selects named world-renowned frameworks, scores the subject across 6 dimensions, challenges its own conclusions, and emits a professional deliverable with a prioritized improvement roadmap.

## Problem Statement
Most actors cannot measure or reduce their carbon footprint credibly. This skill quantifies energy/carbon use, scores sustainability, and produces a prioritized decarbonization roadmap using recognized standards.

Domain context: practitioners in science, engineering & industry need decisions grounded in citable, current methodology rather than ad-hoc opinion. This skill enforces the evidence hierarchy (Systematic Review > Meta-Analysis > RCT > Cohort > Expert Opinion > Blog) and keeps its knowledge current through a weekly crawl.

## Target Users & Use Cases
- **Trigger example A:** User says *"Evaluate / score / optimize my energy/carbon footprint optimizer"* → skill runs the full harness and returns a scored report + roadmap.
- **Trigger example B:** User provides an artifact (document, dataset, design, plan) → skill audits it against the frameworks below.
- **Trigger example C:** User asks *"What should I improve first?"* → skill returns the impact/effort-ranked roadmap section only.

## Harness Architecture
```
USER INPUT
   |
   v
[Stage 1] sub-evaluation-framework-selector  --> scoped profile / context
   |
   v
[Stage 2] sub-scoring-engine  --> selected frameworks (GHG Protocol (Scope 1/2/3), ...)
   |
   v
[Stage 3] RESEARCH (WebSearch/WebFetch) --> evidence pack  (fallback: SECOND-KNOWLEDGE-BRAIN.md)
   |
   v
[Stage 4] sub-improvement-roadmap  --> 6-dimension score
   |
   v
[Stage 5] sub-compliance-check  --> challenge / validation
   |
   v
[COMPLIANCE GATE] sub-compliance-check --> block output until pass
   |
   v
[Stage 6] MAIN HARNESS --> final deliverable (score table + prioritized roadmap)
```

## Full Sub-Skill Catalog

### sub-evaluation-framework-selector
- **Purpose:** Set the boundary (individual/household/SME) and applicable GHG Protocol scopes.
- **Inputs:** scoped context from prior stage + user artifact
- **Outputs:** structured findings passed to the next stage
- **Tools used:** Read, WebSearch, WebFetch, Write
- **Quality gate:** output must be evidence-linked and complete before the harness advances

### sub-scoring-engine
- **Purpose:** Quantify emissions and score sustainability across the six dimensions.
- **Inputs:** scoped context from prior stage + user artifact
- **Outputs:** structured findings passed to the next stage
- **Tools used:** Read, WebSearch, WebFetch, Write
- **Quality gate:** output must be evidence-linked and complete before the harness advances

### sub-improvement-roadmap
- **Purpose:** Build a MACC-ordered decarbonization roadmap (reduce-substitute-offset).
- **Inputs:** scoped context from prior stage + user artifact
- **Outputs:** structured findings passed to the next stage
- **Tools used:** Read, WebSearch, WebFetch, Write
- **Quality gate:** output must be evidence-linked and complete before the harness advances

### sub-compliance-check
- **Purpose:** Validate claims against GHG Protocol/SBTi to avoid greenwashing before output.
- **Inputs:** scoped context from prior stage + user artifact
- **Outputs:** structured findings passed to the next stage
- **Tools used:** Read, WebSearch, WebFetch, Write
- **Quality gate:** output must be evidence-linked and complete before the harness advances

## Skill File Format Specification
Frontmatter schema (all skill files):
```yaml
---
name: energy-carbon-footprint-optimizer            # or sub-<name>
description: <one-line summary shown in /help>
---
```
Required sections in `main.md`: Role & Persona, Workflow (Harness Flow), Sub-skills Available, Tools, Output Format, Quality Gates.

## E2E Execution Flow
1. Parse user request and artifact; if ambiguous, ask targeted intake questions.
2. Run `sub-evaluation-framework-selector` to build the scoped profile.
3. Run `sub-scoring-engine` to lock frameworks: GHG Protocol (Scope 1/2/3), ISO 14064 & ISO 50001, Science Based Targets initiative (SBTi), Marginal Abatement Cost Curve (MACC)....
4. Research: issue WebSearch queries (carbon footprint accounting GHG protocol; energy efficiency optimization; science based targets decarbonization); WebFetch top authoritative hits; grade evidence. On failure, fall back to SECOND-KNOWLEDGE-BRAIN.md and label the degradation.
5. Run `sub-improvement-roadmap` to score the 6 dimensions.
6. Run `sub-compliance-check` challenge pass.

7. **COMPLIANCE:** run sub-compliance-check; block until pass.
8. Synthesize the final deliverable.

## Scoring Dimensions
1. Scope 1 direct emissions
2. Scope 2 energy emissions
3. Scope 3 value-chain emissions
4. Energy-efficiency level
5. Renewables & substitution
6. Reduction-target credibility (SBTi)

Each dimension is scored 0–5 with an evidence citation and a one-line justification; the overall score is the weighted mean (weights set by `sub-scoring-engine`).

## SECOND-KNOWLEDGE-BRAIN Integration
- **Sources:** ArXiv (eess.SY, physics.soc-ph); GHG Protocol standards, IPCC emission-factor databases, IEA energy data, arXiv eess.SY (energy systems), CDP & SBTi guidance.
- **Crawl config:** weekly cron via `tools/knowledge_updater.py` (crawl4ai).
- **Append format:** scored entries (title, authors, year, DOI/URL, key finding, relevance) added to the Knowledge Update Log with a date stamp and dedup by URL/DOI hash.

## Supporting Tools Spec
`tools/knowledge_updater.py`:
- **Inputs:** search queries (above), ArXiv categories, last-run timestamp.
- **Outputs:** appended entries in `SECOND-KNOWLEDGE-BRAIN.md`.
- **Schedule:** weekly.

## Quality Gates (must all be TRUE before final output)
- Every dimension scored with a cited source or explicit fallback label.
- At least one framework from the catalog explicitly applied.
- Challenge phase documented (≥3 counter-arguments considered).

- Compliance check passed and logged.
- Roadmap items carry impact + effort ratings.

## Test Scenarios (summary; full set in tests/)
1. Happy-path full audit of a typical science, engineering & industry artifact.
2. Ambiguous/incomplete input → intake clarification path.
3. Offline/degraded mode → graceful fallback to knowledge brain.
4. Regulated/compliance-sensitive input → compliance gate path.
5. Roadmap-only request → returns prioritized recommendations.

## Key Design Decisions
1. Framework-grounded scoring only — no ad-hoc criteria.
2. Research-first with explicit graceful degradation.
3. Mandatory challenge phase before synthesis.
4. Compliance gate precedes output.
5. Self-improving knowledge base via weekly crawl.
