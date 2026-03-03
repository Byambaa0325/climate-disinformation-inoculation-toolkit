"""
Counter-Messaging Module

Generates prebunking and debunking counter-narratives for climate disinformation.

Based on:
  - Inoculation Theory (Cook et al., 2017; van der Linden et al., 2022)
  - The Debunking Handbook 2020 (Lewandowsky et al.)
  - 3-Step Debunking Structure: Fact → Myth flag → Fallacy explanation
  - Technique-based prebunking outperforms claim-based prebunking for novel claims

TODO (requires dataset and evaluation):
  - Implement LLM-based prebunking generation using INJECTION_TEMPLATES
  - Implement BLEURT/BERTScore evaluation pipeline (see 04_counter_messaging_eval.ipynb)
  - Add inoculation effectiveness scoring
  - Integrate with ClimateCheck verified facts for grounding
"""

from typing import Dict, Any, Optional, List

try:
    from claim_taxonomy import TAXONOMY, get_cluster
except ImportError:
    from .claim_taxonomy import TAXONOMY, get_cluster


# ─────────────────────────────────────────────────────────────────────────────
# Prebunking templates (technique inoculation approach)
# van der Linden et al. (2022): technique inoculation outperforms fact inoculation
# ─────────────────────────────────────────────────────────────────────────────

PREBUNKING_TEMPLATES: Dict[str, str] = {
    "denial": (
        "Warning: You may encounter a common disinformation technique called "
        "'Fake Experts' or 'Trend Skepticism' (FLICC framework). "
        "This technique manufactures doubt by citing fringe scientists or "
        "misrepresenting historical temperature data. "
        "The scientific consensus — based on 97%+ of publishing climate scientists "
        "across every major national academy of science — is that current warming "
        "is unprecedented in the last 2,000 years and is caused by human greenhouse gases."
    ),
    "doubt_casting": (
        "Warning: You may encounter 'Cherry Picking' or 'Impossible Expectations' — "
        "two FLICC-identified techniques that selectively use data to manufacture doubt. "
        "Cherry picking involves highlighting short-term anomalies (like the 2000s "
        "warming slowdown) while ignoring the long-term trend. "
        "Impossible expectations demand certainty that no empirical science can provide. "
        "Uncertainty in one parameter (e.g., cloud feedbacks) does not invalidate "
        "the overall conclusion — in fact, uncertainty usually means warming could be "
        "higher, not lower."
    ),
    "deflection": (
        "Warning: You may encounter 'Whataboutism' or responsibility deflection — "
        "shifting attention to other countries or individuals to avoid systemic action. "
        "This is a logical fallacy (red herring) because: (1) cumulative historical "
        "emissions from the US and EU exceed China's; (2) per-capita emissions in "
        "developing nations remain far lower; (3) individual and systemic action "
        "are complementary. Deflection does not change the physics of CO2."
    ),
    "delay": (
        "Warning: You may encounter 'Tech Salvation' or 'Moving Goalposts' — "
        "delay tactics that accept climate change but argue action is premature. "
        "IPCC AR6 shows that every decade of delay roughly doubles eventual mitigation "
        "costs. Carbon capture at scale remains unproven; fusion has been '30 years "
        "away' for 60 years. The economic case for immediate action is stronger than "
        "the case for waiting (Stern Review; IPCC AR6 mitigation report)."
    ),
    "conspiracy": (
        "Warning: You may encounter 'Nefarious Intent' framing — a conspiracy "
        "technique (FLICC) that attributes climate science to funding bias or "
        "political agendas. This reasoning is logically flawed because: climate "
        "scientists in the US, EU, China, Russia, India, and oil-producing nations "
        "independently reach the same conclusions; if it were a conspiracy, "
        "rival governments would be the first to expose it. "
        "Independent replication across adversarial nations is the strongest "
        "possible evidence against coordinated fabrication."
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# Main class
# ─────────────────────────────────────────────────────────────────────────────

class CounterMessagingModule:
    """
    Generates prebunking and debunking counter-narratives.

    Prebunking (inoculation): Warn about the manipulation technique *before*
    the user encounters the disinformation. Most effective for novel claims.

    Debunking (correction): Correct a specific false claim after exposure.
    Uses fact-first framing (Lewandowsky et al., 2021).
    """

    def __init__(self, llm_service=None):
        """
        Args:
            llm_service: Optional LLM service for LLM-based generation.
                         Rule-based templates are used if None.
        """
        self.llm_service = llm_service

    def generate_prebunking(
        self,
        cluster_id: str,
        target_question: Optional[str] = None,
        model_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a prebunking (inoculation) counter-message for a cluster.

        Based on van der Linden et al. (2022): technique inoculation is more
        effective than fact inoculation for novel/unseen claims.

        Args:
            cluster_id: Disinformation cluster (denial, doubt_casting, etc.)
            target_question: Optional context for more targeted prebunking
            model_id: Optional LLM model for enhanced generation

        Returns:
            Dict with prebunking message, technique name, and sources
        """
        cluster_data = get_cluster(cluster_id)

        if self.llm_service and target_question:
            # TODO: Implement LLM-enhanced prebunking
            # Prompt: "Write a 2-sentence inoculation warning for [technique]
            #          before discussing [target_question]. Use fact-first framing."
            pass

        # Rule-based prebunking (always available)
        message = PREBUNKING_TEMPLATES.get(
            cluster_id,
            f"Be aware that content about '{cluster_data['display_name']}' "
            "may use disinformation techniques."
        )

        return {
            "type": "prebunking",
            "cluster_id": cluster_id,
            "cluster_display_name": cluster_data["display_name"],
            "message": message,
            "technique_named": cluster_data["techniques"][0] if cluster_data["techniques"] else None,
            "sources": [
                "van der Linden et al. (2022). Global Challenges.",
                "Cook et al. (2022). FLICC Framework.",
                "Lewandowsky et al. (2021). The Debunking Handbook.",
            ],
            "method": "rule-based template",
        }

    def generate_debunking(
        self,
        claim: str,
        cluster_id: str,
        accurate_info: Optional[str] = None,
        model_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a debunking correction for a specific climate disinformation claim.

        Uses 3-step structure from Lewandowsky et al. (2021):
          Step 1: State the FACT (fact-first framing)
          Step 2: Flag the MYTH as false
          Step 3: Explain the FALLACY/technique used

        Args:
            claim: The disinformation claim to debunk
            cluster_id: Which cluster the claim belongs to
            accurate_info: Optional ground-truth accurate information
            model_id: Optional LLM model for enhanced generation

        Returns:
            Dict with 3-step debunking message and metadata
        """
        cluster_data = get_cluster(cluster_id)
        counter_points = cluster_data.get("counter_talking_points", [])

        if self.llm_service:
            # TODO: Implement LLM-based debunking
            # Prompt structure:
            # "Using the 3-step debunking method (Lewandowsky et al., 2021):
            #  1. State the accurate fact about [topic]
            #  2. Briefly flag the following claim as false: [claim]
            #  3. Explain the [cluster] technique being used
            #  Keep the correction shorter than the myth. Use fact-first framing."
            pass

        # Rule-based debunking
        fact = accurate_info or (counter_points[0] if counter_points else "This claim is not supported by the scientific evidence.")
        myth_flag = f"The claim '{claim[:100]}{'...' if len(claim) > 100 else ''}' is false or misleading."
        fallacy = f"This uses the '{cluster_data['display_name']}' disinformation technique: {cluster_data['description']}"

        message = f"{fact}\n\n{myth_flag}\n\n{fallacy}"

        return {
            "type": "debunking",
            "cluster_id": cluster_id,
            "cluster_display_name": cluster_data["display_name"],
            "original_claim": claim,
            "message": message,
            "steps": {
                "step1_fact": fact,
                "step2_myth_flag": myth_flag,
                "step3_fallacy": fallacy,
            },
            "counter_talking_points": counter_points,
            "sources": [
                "Lewandowsky et al. (2021). The Debunking Handbook 2020.",
                "IPCC AR6 (2021). Sixth Assessment Report.",
            ],
            "method": "rule-based 3-step debunking",
        }

    def get_counter_talking_points(self, cluster_id: str) -> List[str]:
        """Return pre-written counter-talking-points for a cluster."""
        return get_cluster(cluster_id).get("counter_talking_points", [])


if __name__ == "__main__":
    module = CounterMessagingModule()

    print("=== PREBUNKING EXAMPLE ===")
    prebunk = module.generate_prebunking("doubt_casting")
    print(f"Cluster: {prebunk['cluster_display_name']}")
    print(f"Message: {prebunk['message']}")

    print("\n=== DEBUNKING EXAMPLE ===")
    debunk = module.generate_debunking(
        claim="Climate models have been consistently wrong, so we shouldn't trust their predictions.",
        cluster_id="doubt_casting",
    )
    print(f"Step 1 (Fact): {debunk['steps']['step1_fact']}")
    print(f"Step 2 (Myth): {debunk['steps']['step2_myth_flag']}")
    print(f"Step 3 (Fallacy): {debunk['steps']['step3_fallacy']}")
