---
name: sub-improvement-roadmap
description: (energy-carbon-footprint-optimizer) Build a MACC-ordered decarbonization roadmap (reduce–substitute–offset).
---

# Sub-skill: improvement-roadmap

## Purpose
Build a MACC-ordered decarbonization roadmap (reduce–substitute–offset) and rank recommendations by impact × effort.

## When the Harness Calls This
Stage 5 of the `energy-carbon-footprint-optimizer` main workflow.

## Inputs
- Scoped context and dimension scores from the scoring engine.
- Entity type and energy/emission profile.

## Procedure
1. Read the incoming context and scores.
2. Apply `src/energy_carbon_footprint_optimizer/improvement_roadmap.py::build_roadmap`.
3. Generate a default lever set aligned with the Energy hierarchy:
   - **Reduce:** energy audits, insulation/setpoint optimisation, travel reduction.
   - **Substitute:** renewable electricity PPAs, electrification, green suppliers.
   - **Offset:** high-integrity carbon removals for residual emissions only.
4. Rank by priority score = `impact_weight × effort_weight`, with category tie-breaking `reduce > substitute > offset`.
   - High impact + low effort ranks first.
5. Annotate every item with impact (H/M/L), effort (H/M/L), cost level, framework basis and estimated emissions reduction.

## Outputs
- `List[RoadmapItem]` passed to the synthesis stage.
- Explicit framework basis for each recommendation.

## Quality Gate
- Output is complete, evidence-linked, and within scope.
- Roadmap items carry impact + effort ratings.
- Ranking follows the reduce–substitute–offset hierarchy.
