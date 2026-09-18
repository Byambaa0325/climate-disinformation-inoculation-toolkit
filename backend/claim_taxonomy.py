"""
Unified Climate Disinformation Taxonomy

Merges three established frameworks into 5 clusters:
  - FLICC (Cook et al., 2022): Fake Experts, Logical Fallacies,
    Impossible Expectations, Cherry Picking, Conspiracy Theories
  - CARDS v2 (Touzel et al., 2023): 11-label hierarchical taxonomy
  - 4D Framework: Deny, Deceive, Deflect, Delay

See data/unified_taxonomy.json for the full crosswalk.
"""

from typing import Dict, List, Any


# ─────────────────────────────────────────────────────────────────────────────
# Core taxonomy structure
# ─────────────────────────────────────────────────────────────────────────────

TAXONOMY: Dict[str, Dict[str, Any]] = {
    "denial": {
        "display_name": "Denial",
        "description": (
            "Direct factual rejection of established climate science — "
            "claiming the phenomenon does not exist, is not occurring, or "
            "is not caused by humans."
        ),
        "source_frameworks": ["FLICC: Fake Experts", "CARDS: Trend/Attribution skepticism", "4D: Deny"],
        "techniques": [
            "fake_experts",
            "trend_skepticism",
            "attribution_skepticism",
            "impersonating_consensus",
        ],
        "keywords": [
            "scientists disagree", "natural cycles", "medieval warm period",
            "not proven", "no consensus", "oregon petition", "cooling not warming",
            "temperature plateau", "ice age coming", "sun causes warming",
            "volcanoes not humans", "co2 is plant food", "slight warming beneficial",
        ],
        "patterns": [
            r"scientists\s+(?:don\'t|do not|disagree|debate|dispute)\s+(?:agree|consensus)",
            r"(?:no|not a)\s+(?:scientific\s+)?consensus",
            r"natural\s+(?:cycle|variation|warming|climate change)",
            r"(?:sun|solar)\s+(?:causes?|drives?|responsible)",
            r"co2\s+(?:is\s+)?(?:not|isn\'t)\s+(?:a\s+)?(?:pollutant|problem|dangerous)",
        ],
        "example_claims": [
            "Many respected geologists actually disagree about whether global temperatures have meaningfully risen over the past century.",
            "The historical record shows that the Medieval Warm Period was warmer than today, without any human CO2.",
            "Isn't it true that thousands of scientists signed the Oregon Petition challenging the climate consensus?",
        ],
        "counter_talking_points": [
            "97%+ of actively publishing climate scientists agree on human-caused warming (Cook et al., 2013; Lynas et al., 2021).",
            "The Medieval Warm Period was regional (Northern Hemisphere) and cooler globally than today.",
            "The Oregon Petition was not peer-reviewed; signatories included non-scientists and fake entries.",
        ],
        "color": "#D32F2F",  # Red
    },

    "doubt_casting": {
        "display_name": "Doubt-Casting",
        "description": (
            "Undermining confidence in climate science through logical fallacies, "
            "impossible standards of proof, or cherry-picked data — without outright rejection."
        ),
        "source_frameworks": [
            "FLICC: Logical Fallacies, Impossible Expectations, Cherry Picking",
            "CARDS: Science unreliable",
            "4D: Deceive",
        ],
        "techniques": [
            "cherry_picking",
            "impossible_expectations",
            "false_equivalence",
            "oversimplification",
            "model_attacks",
        ],
        "keywords": [
            "models have been wrong", "uncertainty", "pause", "hiatus",
            "admitted", "even scientists say", "not settled", "just models",
            "predictions failed", "urban heat island", "adjustments",
            "manipulated data", "natural variability explains",
        ],
        "patterns": [
            r"models?\s+(?:have\s+been|were|are)\s+(?:wrong|inaccurate|failed)",
            r"(?:hiatus|pause|slowdown)\s+in\s+(?:warming|temperature)",
            r"(?:even|scientists|experts)\s+admit",
            r"not\s+(?:fully\s+)?settled",
            r"cherry[- ]pick",
            r"urban\s+heat\s+island",
            r"(?:data|temperature)\s+(?:adjust|manipul)",
        ],
        "example_claims": [
            "Given that climate models failed to predict the 2000s warming pause, how much should we trust their long-term projections?",
            "Since scientists themselves admit there's still uncertainty in cloud feedback mechanisms, isn't it premature to base policy on this?",
            "Wasn't 1998 actually warmer than many subsequent years? That seems to contradict the 'unprecedented warming' narrative.",
        ],
        "counter_talking_points": [
            "The 2000s 'pause' was a statistical artifact of cherry-picking 1998 (an El Niño year) as a start point; the underlying trend was uninterrupted.",
            "Uncertainty in cloud feedbacks means warming could be higher than central estimates, not lower.",
            "Each decade since the 1980s has been warmer than the previous; 2015-2024 are all top-10 warmest years on record.",
        ],
        "color": "#F57C00",  # Orange
    },

    "deflection": {
        "display_name": "Deflection",
        "description": (
            "Accepting climate change but shifting moral or practical responsibility "
            "to other actors, nations, or external forces."
        ),
        "source_frameworks": [
            "CARDS: Fossil fuels necessary, Individual action can't fix it",
            "4D: Deflect",
        ],
        "techniques": [
            "other_countries",
            "whataboutism",
            "individual_responsibility_transfer",
            "fossil_fuel_necessity",
        ],
        "keywords": [
            "china emits", "india", "developing nations", "other countries first",
            "if you really cared", "individual choices", "hypocrisy",
            "fossil fuels needed", "energy security", "economic development",
            "not our problem", "global responsibility",
        ],
        "patterns": [
            r"china\s+(?:emits?|produces?|responsible)",
            r"(?:india|developing)\s+(?:nations?|countries?)\s+(?:still|are|won\'t)",
            r"(?:if\s+you|why\s+don\'t\s+you)\s+(?:really\s+)?(?:care|cared|stop|quit)",
            r"(?:energy|economic)\s+security",
            r"(?:poorest|developing)\s+(?:nations?|countries?)\s+(?:need|deserve|right)",
        ],
        "example_claims": [
            "Since China emits twice as much CO2 as the US, isn't it unfair to expect Western countries to bear the economic burden of transition?",
            "When developing nations are still industrializing, doesn't asking them to cut emissions condemn their populations to poverty?",
            "If you really cared about emissions, you'd stop flying and driving before advocating for broad policy changes.",
        ],
        "counter_talking_points": [
            "The US and EU are responsible for ~50% of all cumulative CO2 since industrialization; China's per-capita emissions remain lower than the US.",
            "The Paris Agreement explicitly provides for 'common but differentiated responsibilities'; developing nations receive climate finance.",
            "Individual action and systemic policy change are complementary, not mutually exclusive; systemic change is ~100x more impactful at scale.",
        ],
        "color": "#7B1FA2",  # Purple
    },

    "delay": {
        "display_name": "Delay",
        "description": (
            "Accepting climate change as real but arguing against current or specific action — "
            "usually in favor of future technology, gradual transition, or economic caution."
        ),
        "source_frameworks": [
            "CARDS: Climate policies harmful, Clean energy won't work, Solutions unrealistic",
            "4D: Delay",
        ],
        "techniques": [
            "tech_salvation",
            "economic_cost",
            "moving_goalposts",
            "false_urgency_reversal",
        ],
        "keywords": [
            "future technology", "wait for", "nuclear fusion", "carbon capture",
            "too expensive", "economic damage", "transition costs",
            "gradual", "realistic timeline", "not yet ready",
            "jobs at risk", "energy prices", "premature",
        ],
        "patterns": [
            r"(?:wait|waiting)\s+for\s+(?:better|new|future|advanced)\s+technology",
            r"(?:nuclear\s+fusion|carbon\s+capture|geoengineering)\s+(?:will|could|soon)",
            r"(?:too|too\s+much|excessive)\s+(?:expensive|cost|economic)",
            r"(?:jobs?|employment|workers?)\s+(?:at\s+risk|will\s+be\s+lost|threatened)",
            r"(?:energy|electricity)\s+prices?\s+(?:will|would)\s+(?:rise|spike|increase)",
            r"(?:premature|too\s+fast|too\s+soon|unrealistic\s+timeline)",
        ],
        "example_claims": [
            "Isn't it wiser to wait for fusion power or next-generation nuclear before committing to costly renewable mandates?",
            "Given the economic impact on energy-dependent communities, shouldn't we allow a more gradual 40-year transition?",
            "With carbon capture technology advancing rapidly, do we really need such drastic immediate cuts to emissions?",
        ],
        "counter_talking_points": [
            "Fusion has been '30 years away' for 60 years; IPCC models require deep cuts by 2030 — carbon capture at scale is unproven.",
            "Every decade of delay doubles the eventual cost of mitigation; IPCC AR6 shows immediate action is economically optimal.",
            "Carbon capture cannot remove carbon faster than continued emissions add it at current technology readiness levels.",
        ],
        "color": "#0288D1",  # Blue
    },

    "conspiracy": {
        "display_name": "Conspiracy",
        "description": (
            "Framing climate science as a coordinated malicious conspiracy involving "
            "governments, scientists, financial interests, or international bodies."
        ),
        "source_frameworks": [
            "FLICC: Conspiracy Theories (all 4 sub-types)",
            "CARDS: Climate movement is conspiracy",
            "LOCO corpus: climate conspiracy narratives",
        ],
        "techniques": [
            "nefarious_intent",
            "global_conspiracy",
            "coverup",
            "persecution_narrative",
        ],
        "keywords": [
            "grant money", "funding bias", "agenda", "great reset",
            "wef", "globalists", "population control", "new world order",
            "silenced scientists", "suppressed data", "climategate",
            "political agenda", "power grab", "follow the money",
            "green new deal propaganda",
        ],
        "patterns": [
            r"(?:follow|following)\s+the\s+money",
            r"(?:government|un|wef|globalist)\s+(?:agenda|control|takeover|plot)",
            r"scientists?\s+(?:are\s+paid|funded)\s+to",
            r"great\s+reset",
            r"climate(?:gate)?",
            r"(?:silenced?|suppressed?|censored?)\s+(?:scientists?|data|evidence|research)",
            r"(?:persecution|attacked|defunded)\s+(?:for|because)\s+(?:questioning|skeptic)",
        ],
        "example_claims": [
            "It's interesting that virtually all climate scientists receive government funding — doesn't that create massive incentive to confirm the narrative that justifies more government spending?",
            "When the IPCC is fundamentally a political body, not a scientific one, how can we trust its conclusions are unbiased?",
            "Given that the Great Reset agenda explicitly links climate policy to economic restructuring, isn't climate change being used as a pretext for global governance?",
        ],
        "counter_talking_points": [
            "Climate scientists in the US, EU, China, Russia, India, and oil-producing nations all independently reach the same conclusions.",
            "The IPCC reports summarize thousands of independently funded peer-reviewed studies; the summary for policymakers is separate from the scientific assessment.",
            "The Great Reset is a World Economic Forum post-COVID recovery initiative; climate scientists are not WEF members or policy advocates.",
        ],
        "color": "#5D4037",  # Brown
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# Access functions
# ─────────────────────────────────────────────────────────────────────────────

def get_cluster(cluster_id: str) -> Dict[str, Any]:
    """Get a single cluster definition by ID."""
    if cluster_id not in TAXONOMY:
        raise ValueError(
            f"Unknown cluster '{cluster_id}'. "
            f"Available clusters: {list(TAXONOMY.keys())}"
        )
    return TAXONOMY[cluster_id]


def get_all_clusters() -> Dict[str, Dict[str, Any]]:
    """Return the full taxonomy."""
    return TAXONOMY


def get_cluster_ids() -> List[str]:
    """Return list of cluster IDs."""
    return list(TAXONOMY.keys())


def get_techniques_for_cluster(cluster_id: str) -> List[str]:
    """Return the list of technique IDs for a cluster."""
    return get_cluster(cluster_id)["techniques"]


def get_all_techniques() -> Dict[str, str]:
    """Return mapping of technique_id → cluster_id for every technique."""
    result = {}
    for cluster_id, cluster_data in TAXONOMY.items():
        for technique in cluster_data["techniques"]:
            result[technique] = cluster_id
    return result


def get_keywords_for_cluster(cluster_id: str) -> List[str]:
    """Return keyword list for a cluster."""
    return get_cluster(cluster_id)["keywords"]


def get_example_claims(cluster_id: str) -> List[str]:
    """Return example disinformation priming questions for a cluster."""
    return get_cluster(cluster_id)["example_claims"]


def get_counter_talking_points(cluster_id: str) -> List[str]:
    """Return counter-messaging talking points for a cluster."""
    return get_cluster(cluster_id)["counter_talking_points"]


def get_taxonomy_for_ui() -> List[Dict[str, Any]]:
    """Return taxonomy formatted for frontend display (without raw patterns)."""
    result = []
    for cluster_id, data in TAXONOMY.items():
        result.append({
            "id": cluster_id,
            "display_name": data["display_name"],
            "description": data["description"],
            "source_frameworks": data["source_frameworks"],
            "techniques": data["techniques"],
            "technique_count": len(data["techniques"]),
            "color": data["color"],
            "example_claims": data["example_claims"][:1],  # First example only for UI
        })
    return result


if __name__ == "__main__":
    print(f"Taxonomy loaded: {len(TAXONOMY)} clusters")
    for cid, cluster in TAXONOMY.items():
        print(f"  {cid}: {len(cluster['techniques'])} techniques, "
              f"{len(cluster['keywords'])} keywords")
