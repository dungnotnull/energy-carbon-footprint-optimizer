from typing import List
from .constants import EntityType, Impact, Effort
from .models import DimensionScore, RoadmapItem, ScoringInput


IMPACT_WEIGHT = {Impact.HIGH: 3, Impact.MEDIUM: 2, Impact.LOW: 1}
EFFORT_WEIGHT = {Effort.HIGH: 1, Effort.MEDIUM: 2, Effort.LOW: 3}
CATEGORY_ORDER = {"reduce": 0, "substitute": 1, "offset": 2}


def _base_levers(entity_type: EntityType) -> List[RoadmapItem]:
    '''Return a default set of MACC-ordered decarbonisation levers.'''
    reduce = [
        RoadmapItem(
            recommendation="Conduct an energy audit and implement no/low-cost efficiency measures",
            impact=Impact.HIGH,
            effort=Effort.LOW,
            cost_level="Low / negative cost",
            framework_basis="ISO 50001 + Energy hierarchy (reduce)",
            emissions_reduction_kg=1500.0,
            payback_years=0.5,
            category="reduce",
        ),
        RoadmapItem(
            recommendation="Optimise heating/cooling setpoints and improve insulation",
            impact=Impact.HIGH,
            effort=Effort.LOW,
            cost_level="Low",
            framework_basis="Energy hierarchy (reduce) + IPCC emission factors",
            emissions_reduction_kg=1200.0,
            payback_years=1.0,
            category="reduce",
        ),
        RoadmapItem(
            recommendation="Reduce non-essential business travel and shift to virtual meetings",
            impact=Impact.MEDIUM,
            effort=Effort.LOW,
            cost_level="Low",
            framework_basis="GHG Protocol Scope 3 + Energy hierarchy (reduce)",
            emissions_reduction_kg=800.0,
            payback_years=0.0,
            category="reduce",
        ),
    ]

    substitute = [
        RoadmapItem(
            recommendation="Procure renewable electricity via green tariff or corporate PPA",
            impact=Impact.HIGH,
            effort=Effort.MEDIUM,
            cost_level="Moderate",
            framework_basis="GHG Protocol Scope 2 + SBTi",
            emissions_reduction_kg=2000.0,
            payback_years=2.0,
            category="substitute",
        ),
        RoadmapItem(
            recommendation="Electrify fleet and heat using renewable-powered systems",
            impact=Impact.HIGH,
            effort=Effort.HIGH,
            cost_level="High",
            framework_basis="IPCC emission factors + Energy hierarchy (substitute)",
            emissions_reduction_kg=2500.0,
            payback_years=4.0,
            category="substitute",
        ),
        RoadmapItem(
            recommendation="Switch to green suppliers and low-carbon procurement",
            impact=Impact.MEDIUM,
            effort=Effort.MEDIUM,
            cost_level="Moderate",
            framework_basis="GHG Protocol Scope 3 + LCA",
            emissions_reduction_kg=1200.0,
            payback_years=1.5,
            category="substitute",
        ),
    ]

    offset = [
        RoadmapItem(
            recommendation="Purchase high-integrity carbon removals for residual emissions only",
            impact=Impact.LOW,
            effort=Effort.MEDIUM,
            cost_level="Variable",
            framework_basis="SBTi Net-Zero Standard + Energy hierarchy (offset)",
            emissions_reduction_kg=500.0,
            payback_years=None,
            category="offset",
        ),
    ]

    # Individual/household variants.
    if entity_type in {EntityType.INDIVIDUAL, EntityType.HOUSEHOLD}:
        reduce[2].recommendation = "Reduce car use and choose active/public transport"
        substitute[1].recommendation = "Install heat-pump or solar PV where feasible"
        substitute[1].effort = Effort.MEDIUM

    return reduce + substitute + offset


def build_roadmap(inp: ScoringInput, dimension_scores: List[DimensionScore]) -> List[RoadmapItem]:
    '''Build a prioritised MACC-ordered roadmap.'''
    scores = {d.dimension: d.score for d in dimension_scores}
    items = _base_levers(inp.entity_type)

    # Boost levers that address the weakest dimensions.
    weak_dimensions = {d for d, s in scores.items() if s < 2.5}
    for item in items:
        if (
            "Scope 2" in item.framework_basis and "Scope 2 energy emissions" in weak_dimensions
        ) or (
            "Scope 3" in item.framework_basis and "Scope 3 value-chain emissions" in weak_dimensions
        ):
            item.impact = Impact.HIGH

    def priority(item: RoadmapItem):
        # High impact and low effort score highest; then reduce > substitute > offset.
        return (
            IMPACT_WEIGHT[item.impact] * EFFORT_WEIGHT[item.effort],
            -CATEGORY_ORDER[item.category],
            -IMPACT_WEIGHT[item.impact],
        )

    items.sort(key=priority, reverse=True)
    for i, item in enumerate(items, start=1):
        item.rank = i

    return items
