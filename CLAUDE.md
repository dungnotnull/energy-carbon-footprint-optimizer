# CLAUDE.md — Energy/Carbon Footprint Optimizer (ESG)

**Skill name:** `energy-carbon-footprint-optimizer`
**Tagline:** Energy/Carbon Footprint Optimizer (ESG)
**Source idea:** #83  |  **Cluster:** `science-industry` (Science, Engineering & Industry)
**Current phase:** Phases 0–5 complete. Production code, tests, seeded knowledge brain and cluster shared references are in place.

## Problem This Skill Solves
Most actors cannot measure or reduce their carbon footprint credibly. This skill quantifies energy/carbon use, scores sustainability, and produces a prioritized decarbonization roadmap using recognized standards.

## Harness Flow Summary
1. **Intake / scoping** → `sub-evaluation-framework-selector.md` gathers context and constraints.
2. **Framework selection** → `sub-scoring-engine.md` chooses the named evaluation frameworks for this case.
3. **Research / evidence** → WebSearch + WebFetch pull authoritative sources; fall back to SECOND-KNOWLEDGE-BRAIN.md if offline.
4. **Scoring / analysis** → `sub-improvement-roadmap.md` scores across the 6 dimensions.
5. **Challenge phase** → devil's-advocate review (`sub-compliance-check.md`).
6. **Synthesis** → main harness assembles the final professional deliverable (score + prioritized roadmap).

**Compliance gate:** `sub-compliance-check` MUST pass before the final deliverable is emitted.

## Sub-skills
- `skills/sub-evaluation-framework-selector.md` — Set the boundary (individual/household/SME) and applicable GHG Protocol scopes.
- `skills/sub-scoring-engine.md` — Quantify emissions and score sustainability across the six dimensions.
- `skills/sub-improvement-roadmap.md` — Build a MACC-ordered decarbonization roadmap (reduce-substitute-offset).
- `skills/sub-compliance-check.md` — Validate claims against GHG Protocol/SBTi to avoid greenwashing before output.

## Tools Required
- WebSearch, WebFetch (research-first evidence gathering)
- Read, Write (deliverable assembly)
- Bash / Python (run `tools/knowledge_updater.py`)

## Knowledge Sources
- ArXiv categories: eess.SY, physics.soc-ph
- Domain sources: GHG Protocol standards, IPCC emission-factor databases, IEA energy data, arXiv eess.SY (energy systems), CDP & SBTi guidance

## Supporting Python Tools
- `tools/knowledge_updater.py` — crawl4ai pipeline that refreshes `SECOND-KNOWLEDGE-BRAIN.md` weekly.

## Active Development Tasks
- [x] Scaffold folder + 8 required deliverables
- [x] Define 7 named evaluation frameworks
- [x] Implement 4 sub-skills (min 3)
- [ ] Wire shared cluster sub-skills across `science-industry`
- [ ] First live crawl to seed SECOND-KNOWLEDGE-BRAIN knowledge log

## Reference Docs
- `PROJECT-detail.md` — full technical spec
- `PROJECT-DEVELOPMENT-PHASE-TRACKING.md` — phase roadmap
- `SECOND-KNOWLEDGE-BRAIN.md` — self-improving knowledge base
