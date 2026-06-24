---
name: sub-scoring-engine
description: (energy-carbon-footprint-optimizer) Quantify emissions and score sustainability across the six dimensions.
---

# Sub-skill: scoring-engine

## Purpose
Quantify emissions and score sustainability across the six dimensions using named, citable frameworks.

## When the Harness Calls This
Stage 4 of the `energy-carbon-footprint-optimizer` main workflow.

## Inputs
- Scoped context from `sub-evaluation-framework-selector`.
- User artifact / data: Scope 1, Scope 2, Scope 3 emissions; energy metrics; renewable share; efficiency measures; targets.
- Evidence sources or a degraded-mode flag.

## Procedure
1. Read the incoming context and the artifact.
2. Apply the relevant framework(s) for this stage.
3. Use `src/energy_carbon_footprint_optimizer/scoring_engine.py::score_dimensions`.
4. Each dimension is scored 0–5:
   - **Scope 1/2/3:** combines data completeness (verified vs unverified) and performance against a benchmark.
   - **Energy-efficiency level:** based on energy intensity (kWh/m² or kWh/employee) vs benchmark, plus efficiency measures.
   - **Renewables & substitution:** based on renewable share plus substitution measures (PPA, RECs, heat pumps, EVs).
   - **Reduction-target credibility:** based on target existence, coverage, SBTi validation, net-zero ambition and timeline.
5. Use WebSearch/WebFetch to verify any factual claim; grade evidence by tier.
6. Produce structured `DimensionScore` output for the next stage.

Default dimension weights:
- Scope 1: 0.15
- Scope 2: 0.15
- Scope 3: 0.20
- Energy-efficiency level: 0.20
- Renewables & substitution: 0.15
- Reduction-target credibility (SBTi): 0.15

## Outputs
- `List[DimensionScore]` passed to the next harness stage.
- Explicit citations or a labeled fallback to `SECOND-KNOWLEDGE-BRAIN.md`.

## Quality Gate
- Output is complete, evidence-linked, and within scope.
- No unsupported claims; ready for the next stage.
