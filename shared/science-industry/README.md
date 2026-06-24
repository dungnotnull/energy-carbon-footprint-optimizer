# Shared `science-industry` cluster assets

This directory documents the reusable modules and templates that sibling skills in the `science-industry` cluster can import or reference.

## Contents

- `manifest.json` — machine-readable list of shared modules and install instructions.
- `../skills/shared-cluster-sub-skills.md` — skill-level reference document.
- `../../src/energy_carbon_footprint_optimizer/` — the actual reusable Python package.

## Usage

```bash
# Install the package as an editable dependency in a sibling skill
pip install -e D:\skills\energy-carbon-footprint-optimizer
```

```python
from energy_carbon_footprint_optimizer.harness import run_harness
from energy_carbon_footprint_optimizer.models import ScoringInput, EntityType, EnergyMetrics
```

## Design principle

Cluster skills should not duplicate carbon-accounting, scoring or compliance logic. They should import the shared package and reuse the framework catalog, scoring dimensions and output templates defined here.
