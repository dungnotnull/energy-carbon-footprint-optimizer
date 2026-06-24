# Energy / Carbon Footprint Optimizer (ESG)

Production-grade carbon-accounting and decarbonisation harness for individuals, households and SMEs. Part of the `science-industry` skill cluster.

## What it does

- Selects applicable, named frameworks (GHG Protocol, ISO 14064/50001, SBTi, MACC, Energy hierarchy, LCA, IPCC emission factors).
- Scores six dimensions deterministically from user data and evidence.
- Runs a mandatory devil's-advocate challenge phase.
- Blocks output until a GHG Protocol / SBTi compliance check passes.
- Produces a MACC-ordered, reduce–substitute–offset roadmap.
- Refreshes its knowledge base weekly via `tools/knowledge_updater.py`.

## Quick start

```bash
pip install -r requirements.txt

# Seed the knowledge brain (no network required)
python tools/knowledge_updater.py --seed

# Run tests
pytest

# Run the harness from Python
PYTHONPATH=src python -c "
from energy_carbon_footprint_optimizer.harness import run_harness
from energy_carbon_footprint_optimizer.models import ScoringInput, EntityType, EnergyMetrics
print(run_harness(ScoringInput(
    entity_type=EntityType.HOUSEHOLD,
    name='My home',
    energy=EnergyMetrics(annual_kwh=4000, area_m2=100, renewable_share=0.3),
)))
"
```

## Package layout

```
src/energy_carbon_footprint_optimizer/
  __init__.py               # Public API
  constants.py              # Frameworks, dimensions, benchmarks, evidence tiers
  models.py                 # Pydantic schemas
  framework_selector.py     # Select applicable frameworks
  scoring_engine.py         # 6-dimension scoring logic
  improvement_roadmap.py    # MACC-ordered roadmap builder
  compliance_check.py       # GHG Protocol / SBTi anti-greenwashing gate
  harness.py                # End-to-end orchestration and quality gates
  knowledge_brain.py        # SECOND-KNOWLEDGE-BRAIN.md fallback loader
  cli.py                    # Command-line interface
  __main__.py               # Allows `python -m energy_carbon_footprint_optimizer`

tools/
  knowledge_updater.py      # Weekly knowledge-brain updater (ArXiv + pluggable WebSearch)

tests/
  test_scenarios.py         # 5 scenario tests + regression tests
  test_knowledge_updater.py # Seed / dedup tests

shared/science-industry/
  README.md                 # How sibling skills reuse the package
  manifest.json             # Machine-readable shared-module manifest
```

## CLI usage

```bash
PYTHONPATH=src python -m energy_carbon_footprint_optimizer --input input.json --output report.json
```

## Skill documentation

- `skills/main.md` — harness workflow and output format
- `skills/sub-*.md` — four sub-skill references
- `skills/shared-cluster-sub-skills.md` — cluster reuse guide
- `PROJECT-detail.md` — technical specification
- `PROJECT-DEVELOPMENT-PHASE-TRACKING.md` — phase status

## License

MIT
