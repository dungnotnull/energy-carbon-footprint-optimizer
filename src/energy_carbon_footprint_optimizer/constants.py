from enum import Enum

PACKAGE = "energy_carbon_footprint_optimizer"


class EntityType(str, Enum):
    INDIVIDUAL = "individual"
    HOUSEHOLD = "household"
    SME = "sme"
    OTHER = "other"


class EvidenceTier(str, Enum):
    SYSTEMATIC_REVIEW = "Systematic Review"
    META_ANALYSIS = "Meta-Analysis"
    RCT = "RCT"
    COHORT = "Cohort"
    EXPERT_OPINION = "Expert Opinion"
    BLOG = "Blog"
    FRAMEWORK_DOC = "Framework / Standard document"
    KNOWLEDGE_BRAIN = "SECOND-KNOWLEDGE-BRAIN fallback"


class Impact(str, Enum):
    HIGH = "H"
    MEDIUM = "M"
    LOW = "L"


class Effort(str, Enum):
    HIGH = "H"
    MEDIUM = "M"
    LOW = "L"


# Seven named methodologies / frameworks (ISO pair counted as one named methodology).
FRAMEWORKS = [
    {
        "id": "ghg-protocol",
        "name": "GHG Protocol Corporate Accounting and Reporting Standard",
        "type": "methodology",
        "url": "https://ghgprotocol.org/corporate-standard",
    },
    {
        "id": "iso-14064-50001",
        "name": "ISO 14064 & ISO 50001 (GHG quantification & energy management)",
        "type": "standard",
        "url": "https://www.iso.org/standard/66453.html",
    },
    {
        "id": "sbti",
        "name": "Science Based Targets initiative (SBTi) Corporate Net-Zero Standard",
        "type": "methodology",
        "url": "https://sciencebasedtargets.org/net-zero-standard",
    },
    {
        "id": "macc",
        "name": "Marginal Abatement Cost Curve (MACC)",
        "type": "methodology",
        "url": "https://www.mckinsey.com/capabilities/sustainability/our-insights/curbing-carbon-emissions-a-macc-approach",
    },
    {
        "id": "energy-hierarchy",
        "name": "Energy hierarchy: reduce–substitute–offset",
        "type": "methodology",
        "url": "https://www.cibse.org/knowledge/knowledge-items/detail?id=a0q20000008b3orAAA",
    },
    {
        "id": "lca",
        "name": "Life-Cycle Assessment (LCA)",
        "type": "methodology",
        "url": "https://www.epa.gov/nrmrl/lcaccess/pdfs/1011_lca_principles.pdf",
    },
    {
        "id": "ipcc-emission-factors",
        "name": "IPCC 2019 Refinement to 2006 Guidelines emission factors",
        "type": "data",
        "url": "https://www.ipcc-nggip.iges.or.jp/public/2019rf/index.html",
    },
]

DIMENSIONS = [
    "Scope 1 direct emissions",
    "Scope 2 energy emissions",
    "Scope 3 value-chain emissions",
    "Energy-efficiency level",
    "Renewables & substitution",
    "Reduction-target credibility (SBTi)",
]

DEFAULT_WEIGHTS = {
    "Scope 1 direct emissions": 0.15,
    "Scope 2 energy emissions": 0.15,
    "Scope 3 value-chain emissions": 0.20,
    "Energy-efficiency level": 0.20,
    "Renewables & substitution": 0.15,
    "Reduction-target credibility (SBTi)": 0.15,
}

# Reference benchmarks for scoring performance on a 0–5 scale.
# Values are illustrative order-of-magnitude baselines; real deployments can
# override them via the scoring engine.
BENCHMARKS = {
    EntityType.INDIVIDUAL: {
        "scope1": {"unit": "kgCO2e/person/year", "value": 2000.0},
        "scope2": {"unit": "kgCO2e/person/year", "value": 1500.0},
        "scope3": {"unit": "kgCO2e/person/year", "value": 3000.0},
        "energy_intensity": {"unit": "kWh/person/year", "value": 6000.0},
    },
    EntityType.HOUSEHOLD: {
        "scope1": {"unit": "kgCO2e/household/year", "value": 5000.0},
        "scope2": {"unit": "kgCO2e/household/year", "value": 4000.0},
        "scope3": {"unit": "kgCO2e/household/year", "value": 8000.0},
        "energy_intensity": {"unit": "kWh/m²/year", "value": 150.0},
    },
    EntityType.SME: {
        "scope1": {"unit": "kgCO2e/employee/year", "value": 3000.0},
        "scope2": {"unit": "kgCO2e/employee/year", "value": 2500.0},
        "scope3": {"unit": "kgCO2e/employee/year", "value": 5000.0},
        "energy_intensity": {"unit": "kWh/employee/year", "value": 8000.0},
    },
    EntityType.OTHER: {
        "scope1": {"unit": "kgCO2e/year", "value": 10000.0},
        "scope2": {"unit": "kgCO2e/year", "value": 8000.0},
        "scope3": {"unit": "kgCO2e/year", "value": 15000.0},
        "energy_intensity": {"unit": "kWh/year", "value": 50000.0},
    },
}

EVIDENCE_HIERARCHY = [
    EvidenceTier.SYSTEMATIC_REVIEW,
    EvidenceTier.META_ANALYSIS,
    EvidenceTier.RCT,
    EvidenceTier.COHORT,
    EvidenceTier.EXPERT_OPINION,
    EvidenceTier.BLOG,
]

SEARCH_QUERIES = [
    "carbon footprint accounting GHG protocol",
    "energy efficiency optimization",
    "science based targets decarbonization",
]

ARXIV_CATEGORIES = ["eess.SY", "physics.soc-ph"]

DOMAIN_KEYWORDS = ['carbon', 'energy', 'science', 'decarbonization', 'footprint']

