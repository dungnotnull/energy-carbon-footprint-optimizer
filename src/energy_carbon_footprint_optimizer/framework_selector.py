from typing import List
from .constants import FRAMEWORKS, EntityType
from .models import FrameworkApplication


def select_frameworks(entity_type: EntityType, claims: List[str]) -> List[FrameworkApplication]:
    '''Select the named frameworks that apply to this subject and its claims.'''
    claims_text = " ".join(c.lower() for c in claims)
    selected: List[FrameworkApplication] = []

    def add(framework_id: str, reason: str, scopes=None):
        if any(s.framework_id == framework_id for s in selected):
            return
        fw = next(f for f in FRAMEWORKS if f["id"] == framework_id)
        selected.append(
            FrameworkApplication(
                framework_id=fw["id"],
                name=fw["name"],
                reason=reason,
                scopes=scopes or [],
            )
        )

    # Core methodology for every carbon/energy evaluation.
    add(
        "ghg-protocol",
        "Defines Scope 1/2/3 boundaries and the corporate carbon-accounting baseline.",
        ["1", "2", "3"],
    )
    add(
        "ipcc-emission-factors",
        "Provides the authoritative emission factors applied to activity data.",
        ["1", "2", "3"],
    )
    add(
        "energy-hierarchy",
        "Prioritises actions in reduce–substitute–offset order.",
        [],
    )

    # Organisation-level or complex subjects need ISO and SBTi rigour.
    if entity_type in {EntityType.SME, EntityType.OTHER}:
        add(
            "iso-14064-50001",
            "Organisation-level GHG quantification, reporting and energy-management systems.",
            ["1", "2", "3"],
        )
        add(
            "sbti",
            "Ensures reduction targets are consistent with climate science (1.5 °C pathway).",
            [],
        )

    # Product / life-cycle claims trigger LCA.
    if any(k in claims_text for k in ("product", "lifecycle", "lca", "cradle", "grave")):
        add(
            "lca",
            "Needed when the evaluation boundary is a product or service life cycle.",
            [],
        )

    # Abatement / net-zero / offset / carbon-neutral claims trigger MACC and SBTi validation.
    if any(
        k in claims_text
        for k in ("net-zero", "net zero", "carbon neutral", "climate neutral", "offset", "abatement", "macc")
    ):
        add(
            "macc",
            "Ranks decarbonisation options by cost-effectiveness for abatement planning.",
            [],
        )
        add(
            "sbti",
            "Required to validate net-zero or carbon-neutral ambition with science-based criteria.",
            [],
        )

    return selected
