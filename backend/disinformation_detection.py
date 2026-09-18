"""
Disinformation Detection Module

Rule-based and pattern-based detection of climate disinformation techniques.
Classifies text into the 5-cluster unified taxonomy:
  denial | doubt_casting | deflection | delay | conspiracy

Based on:
  - FLICC Framework (Cook et al., 2022)
  - CARDS v2 taxonomy (Touzel et al., 2023)
  - 4D Framework (Stoddart & Tindall, 2020)

See data/unified_taxonomy.json for the full framework crosswalk.
"""

import re
from typing import Dict, List, Any, Optional

try:
    from claim_taxonomy import TAXONOMY, get_cluster_ids
except ImportError:
    from .claim_taxonomy import TAXONOMY, get_cluster_ids


class DisinformationDetector:
    """
    Detects climate disinformation techniques in text using rule-based matching.

    Aligned with:
    - FLICC Framework (Cook et al., 2022): 5 super-categories, 22 sub-techniques
    - CARDS v2 (Touzel et al., 2023): 11 hierarchical labels
    - 4D Framework: Deny, Deceive, Deflect, Delay postures
    """

    def detect(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for climate disinformation signals.

        Args:
            text: Input text (LLM response, user prompt, or article excerpt)

        Returns:
            Dictionary with per-cluster scores, detected techniques,
            overall severity, and framework alignments.
        """
        text_lower = text.lower()
        results: Dict[str, Any] = {
            "cluster_scores": {},
            "detected_techniques": [],
            "matched_phrases": [],
            "overall_score": 0.0,
            "primary_cluster": None,
            "severity": "none",
            "framework_alignments": [],
        }

        cluster_scores: Dict[str, float] = {}

        for cluster_id, cluster_data in TAXONOMY.items():
            score, matches, phrases = self._score_cluster(
                text_lower, cluster_id, cluster_data
            )
            cluster_scores[cluster_id] = score

            if score > 0:
                results["detected_techniques"].extend(matches)
                results["matched_phrases"].extend(phrases)
                if cluster_data["source_frameworks"]:
                    results["framework_alignments"].extend(
                        [f.split(":")[0] for f in cluster_data["source_frameworks"]]
                    )

        results["cluster_scores"] = cluster_scores

        # Overall score = weighted sum (higher weight for more severe clusters)
        weights = {
            "conspiracy": 0.30,
            "denial": 0.25,
            "doubt_casting": 0.20,
            "delay": 0.15,
            "deflection": 0.10,
        }
        total = sum(cluster_scores.get(c, 0) * w for c, w in weights.items())
        results["overall_score"] = min(1.0, total)

        # Primary cluster = highest scoring
        if any(v > 0 for v in cluster_scores.values()):
            results["primary_cluster"] = max(cluster_scores, key=cluster_scores.get)

        # Severity
        score = results["overall_score"]
        if score < 0.1:
            results["severity"] = "none"
        elif score < 0.3:
            results["severity"] = "low"
        elif score < 0.5:
            results["severity"] = "medium"
        elif score < 0.75:
            results["severity"] = "high"
        else:
            results["severity"] = "severe"

        # Deduplicate
        results["framework_alignments"] = list(set(results["framework_alignments"]))

        return results

    # ──────────────────────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _score_cluster(
        self,
        text_lower: str,
        cluster_id: str,
        cluster_data: Dict[str, Any],
    ):
        """
        Score a single cluster against the text.

        Returns:
            (score: float, matched_techniques: list, matched_phrases: list)
        """
        keyword_hits: List[str] = []
        pattern_hits: List[str] = []

        # Keyword matching
        for kw in cluster_data.get("keywords", []):
            if kw in text_lower:
                keyword_hits.append(kw)

        # Regex pattern matching
        for pattern in cluster_data.get("patterns", []):
            try:
                match = re.search(pattern, text_lower)
                if match:
                    pattern_hits.append(match.group(0))
            except re.error:
                pass

        total_hits = len(keyword_hits) + len(pattern_hits)
        if total_hits == 0:
            return 0.0, [], []

        # Score: diminishing returns after 3 hits (to prevent domination by long texts)
        raw = total_hits / (total_hits + 3)
        score = min(1.0, raw)

        techniques = []
        if keyword_hits or pattern_hits:
            techniques.append({
                "cluster": cluster_id,
                "display_name": cluster_data["display_name"],
                "keyword_hits": keyword_hits[:5],   # cap display
                "pattern_hits": pattern_hits[:3],
                "confidence": round(score, 3),
                "framework": cluster_data["source_frameworks"][0] if cluster_data["source_frameworks"] else "",
            })

        matched_phrases = keyword_hits[:5] + pattern_hits[:3]
        return score, techniques, matched_phrases

    def get_explanation(self, cluster_id: str) -> str:
        """Return a human-readable explanation for a detected cluster."""
        explanations = {
            "denial": (
                "Denial (FLICC: Fake Experts; CARDS: Trend/Attribution skepticism): "
                "The text contains signals consistent with direct factual rejection of "
                "climate science, including references to scientific disagreement, natural "
                "causes, or historical temperature comparisons used to dismiss current trends."
            ),
            "doubt_casting": (
                "Doubt-Casting (FLICC: Logical Fallacies, Cherry Picking; CARDS: Science unreliable): "
                "The text uses epistemic uncertainty, model failures, or cherry-picked data "
                "to undermine confidence in climate science without outright denial."
            ),
            "deflection": (
                "Deflection (CARDS: Fossil fuels necessary; 4D: Deflect): "
                "The text shifts responsibility for climate action to other nations, "
                "individuals, or economic necessity, avoiding engagement with systemic solutions."
            ),
            "delay": (
                "Delay (CARDS: Clean energy won't work, Policies harmful; 4D: Delay): "
                "The text accepts climate change but argues against current action, "
                "emphasizing future technology, economic costs, or unrealistic timelines."
            ),
            "conspiracy": (
                "Conspiracy (FLICC: Conspiracy Theories; CARDS: Climate movement conspiracy): "
                "The text attributes climate science to coordinated malicious actors, "
                "funding bias, political agendas, or global governance schemes."
            ),
        }
        return explanations.get(cluster_id, "Unknown cluster.")


def detect_disinformation(text: str) -> Dict[str, Any]:
    """Convenience function for one-shot detection."""
    detector = DisinformationDetector()
    return detector.detect(text)


if __name__ == "__main__":
    detector = DisinformationDetector()

    test_cases = [
        "Given that climate models failed to predict the warming pause, how confident can we really be in their projections?",
        "Since China emits far more than Europe, isn't it unreasonable to ask European workers to pay for an energy transition?",
        "It's interesting that climate scientists all depend on government grants — doesn't that create obvious incentive bias?",
        "The scientific evidence shows global average temperatures have risen approximately 1.1°C since pre-industrial times.",
    ]

    for text in test_cases:
        result = detector.detect(text)
        print(f"\nText: {text[:80]}...")
        print(f"  Primary cluster: {result['primary_cluster']}")
        print(f"  Severity: {result['severity']}")
        print(f"  Score: {result['overall_score']:.2f}")
        print(f"  Matched phrases: {result['matched_phrases'][:3]}")
