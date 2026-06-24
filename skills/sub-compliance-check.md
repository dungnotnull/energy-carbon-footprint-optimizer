---
name: sub-compliance-check
description: (energy-carbon-footprint-optimizer) Validate claims against GHG Protocol/SBTi to avoid greenwashing before output.
---

# Sub-skill: compliance-check

## Purpose
Validate claims against GHG Protocol / SBTi to avoid greenwashing and block output until all blocking issues are resolved.

## When the Harness Calls This
Challenge phase and compliance gate of the `energy-carbon-footprint-optimizer` main workflow.

## Inputs
- Scoped context from prior stages.
- User claims (e.g., "carbon neutral", "net-zero", "offset").
- Emission scopes, targets, selected frameworks, and dimension scores.

## Procedure
1. Read the incoming context and deliverable.
2. Apply `src/energy_carbon_footprint_optimizer/compliance_check.py::run_compliance`.
3. Blocking checks:
   - Net-zero / carbon-neutral claims require an SBTi-validated (or equivalent) target.
   - Net-zero / carbon-neutral claims require a documented net-zero target year and abatement pathway.
   - Offset-based neutrality claims may only cover residual emissions after science-based abatement.
4. Warning checks:
   - Material Scope 3 (>40% of total) requires disclosure of categories and methodology.
   - High scores based only on self-reported data need independent verification.
   - Organisation-level subjects should align with ISO 14064 / ISO 50001.
5. Add required disclaimers, including jurisdiction-specific notes for regulated regions (EU, UK, CA, US, AU, etc.).
6. Return `PASS` only when `blocking_issues` is empty; otherwise return the list of blocking issues.

## ⚖️ Compliance Protocol (blocks output)
The main harness may not emit output until this returns PASS.

## Outputs
- `ComplianceResult` with `passed`, `blocking_issues`, `warnings`, and `disclaimers`.
- Explicit citations or a labeled fallback to `SECOND-KNOWLEDGE-BRAIN.md`.

## Quality Gate
- Output is complete, evidence-linked, and within scope.
- Returns PASS/blocking-issues status.
