---
name: shared-cluster-science-industry
description: Reusable modules and skill references for the science-industry cluster, used by energy-carbon-footprint-optimizer and sibling skills.
---

# Shared Cluster Sub-skills — `science-industry`

## Purpose
Avoid duplicated sub-skill logic across the `science-industry` cluster by centralising the evaluation, scoring, roadmap, and compliance primitives in a reusable Python package.

## Shared Modules
All modules live under `src/energy_carbon_footprint_optimizer/` and are exposed through the package `__init__.py`:

| Module | Public function | Responsibility |
|--------|----------------|----------------|
| `framework_selector.py` | `select_frameworks` | Choose applicable named frameworks based on entity type and claims |
| `scoring_engine.py` | `score_dimensions`, `overall_score` | Score the six dimensions deterministically |
| `improvement_roadmap.py` | `build_roadmap` | Generate a MACC-ordered reduce–substitute–offset roadmap |
| `compliance_check.py` | `run_compliance` | Validate claims against GHG Protocol / SBTi rules |
| `harness.py` | `run_harness` | End-to-end orchestration with intake, challenge and quality gates |
| `knowledge_brain.py` | `load_brain_sources` | Load fallback evidence from `SECOND-KNOWLEDGE-BRAIN.md` |

## How Sibling Skills Can Reuse
1. **Python package dependency:** Add `energy-carbon-footprint-optimizer` as an installable dependency (`pyproject.toml`).
2. **Skill markdown reference:** Import the public functions above into a sibling skill's workflow when the task involves carbon/energy evaluation.
3. **Output template:** Reuse the scoring table and roadmap table formats defined in `skills/main.md#Output Format`.

## Cluster Manifest
See `shared/science-industry/manifest.json` for the machine-readable module list.

## Success Criteria
- No duplicated scoring or compliance logic within the cluster.
- Framework catalog, evidence tiers and output templates are defined once and referenced everywhere.
