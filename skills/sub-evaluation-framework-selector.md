---
name: sub-evaluation-framework-selector
description: (energy-carbon-footprint-optimizer) Set the boundary (individual/household/SME) and applicable GHG Protocol scopes.
---

# Sub-skill: evaluation-framework-selector

## Purpose
Set the boundary (individual/household/SME) and applicable GHG Protocol scopes, then lock the named frameworks that will be used for scoring and compliance.

## When the Harness Calls This
Stage 1 of the `energy-carbon-footprint-optimizer` main workflow.

## Inputs
- The user's artifact and any scoped context from prior stages.
- The subject name/identifier.
- The subject type (`individual`, `household`, `sme`, `other`).
- Region or jurisdiction (optional, used for compliance disclaimers).
- User claims such as "carbon neutral", "net-zero", "product LCA", etc.

## Procedure
1. Read the incoming context and artifact.
2. Validate that the minimum required data is present:
   - `name` is supplied.
   - For `household`: floor area (m²) is supplied or requested.
   - For `sme`: employee count is supplied or requested.
   - At least one Scope 1/2/3 emission value **or** annual energy consumption is supplied.
3. If data is missing, return ≤5 targeted clarification questions and stop.
4. Apply `src/energy_carbon_footprint_optimizer/framework_selector.py::select_frameworks` to choose frameworks:
   - GHG Protocol + IPCC emission factors + Energy hierarchy are always applied.
   - ISO 14064/50001 and SBTi are added for `sme` / `other`.
   - LCA is added when product/lifecycle claims appear.
   - MACC and SBTi are added when net-zero / offset / abatement claims appear.
5. Grade any factual claim by evidence tier.
6. Produce the structured `FrameworkApplication` list for the next stage.

## Outputs
- `List[FrameworkApplication]` passed to the scoring engine.
- Explicit citations or a labeled fallback to `SECOND-KNOWLEDGE-BRAIN.md`.

## Quality Gate
- Output is complete, evidence-linked, and within scope.
- No unsupported claims; ready for the next stage.
