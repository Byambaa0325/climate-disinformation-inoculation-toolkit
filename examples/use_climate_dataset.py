"""
Climate Disinformation Dataset — Usage Examples

Demonstrates how to use the dataset client and taxonomy.
See research/datasets_inventory.md for dataset sources.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from claim_taxonomy import (
    TAXONOMY,
    get_cluster_ids,
    get_example_claims,
    get_counter_talking_points,
    get_taxonomy_for_ui,
)
from disinformation_detection import DisinformationDetector
from disinformation_injection import DisinformationInjector
from counter_messaging import CounterMessagingModule


def example_1_taxonomy_overview():
    """Example 1: Explore the unified taxonomy."""
    print("=" * 60)
    print("EXAMPLE 1: Taxonomy Overview")
    print("=" * 60)

    clusters = get_cluster_ids()
    print(f"Clusters: {clusters}\n")

    for cid in clusters:
        cluster = TAXONOMY[cid]
        print(f"[{cid}] {cluster['display_name']}")
        print(f"  Techniques: {', '.join(cluster['techniques'])}")
        print(f"  Source frameworks: {cluster['source_frameworks']}")
        print()


def example_2_detect_disinformation():
    """Example 2: Detect disinformation in text."""
    print("=" * 60)
    print("EXAMPLE 2: Disinformation Detection")
    print("=" * 60)

    detector = DisinformationDetector()

    test_texts = [
        "Given that climate models failed to predict the 2000s warming pause, should we trust their projections?",
        "Since China emits twice as much as Europe, isn't European climate policy economically self-defeating?",
        "Climate scientists all receive government grants — doesn't that create obvious incentive bias?",
        "Global average temperature has risen approximately 1.1°C since pre-industrial times according to IPCC AR6.",
    ]

    for text in test_texts:
        result = detector.detect(text)
        print(f"Text: {text[:70]}...")
        print(f"  Primary cluster: {result['primary_cluster'] or 'none'}")
        print(f"  Severity: {result['severity']}")
        print(f"  Score: {result['overall_score']:.2f}")
        if result['matched_phrases']:
            print(f"  Matched: {result['matched_phrases'][:2]}")
        print()


def example_3_generate_priming_questions():
    """Example 3: Generate priming questions for a target question."""
    print("=" * 60)
    print("EXAMPLE 3: Priming Question Generation (Rule-Based)")
    print("=" * 60)

    injector = DisinformationInjector(llm_service=None)

    target = "What does scientific evidence show about global temperature trends over the past century?"
    print(f"Target question: {target}\n")

    for cluster_id in get_cluster_ids():
        prime = injector.generate_prime(target, cluster_id)
        print(f"[{cluster_id.upper()}]")
        print(f"  {prime}")
        print()


def example_4_counter_messaging():
    """Example 4: Generate counter-messaging for disinformation claims."""
    print("=" * 60)
    print("EXAMPLE 4: Counter-Messaging")
    print("=" * 60)

    module = CounterMessagingModule()

    claims = {
        "doubt_casting": "Climate models have been consistently wrong, so we shouldn't trust them.",
        "deflection": "China emits so much more that Western action is pointless.",
        "conspiracy": "Climate scientists all depend on government grants that reward certain conclusions.",
    }

    for cluster_id, claim in claims.items():
        print(f"\nCluster: {cluster_id}")
        print(f"Claim: {claim}")
        print()

        # Prebunking (inoculation)
        prebunk = module.generate_prebunking(cluster_id)
        print(f"Prebunking (inoculation):")
        print(f"  {prebunk['message'][:200]}...")
        print()

        # Debunking (3-step correction)
        debunk = module.generate_debunking(claim=claim, cluster_id=cluster_id)
        print(f"Debunking (3-step):")
        print(f"  Step 1 (Fact): {debunk['steps']['step1_fact'][:100]}...")
        print(f"  Step 2 (Myth): {debunk['steps']['step2_myth_flag'][:80]}...")
        print(f"  Step 3 (Fallacy): {debunk['steps']['step3_fallacy'][:80]}...")
        print()


def example_5_example_claims_by_cluster():
    """Example 5: Get example priming questions from the taxonomy."""
    print("=" * 60)
    print("EXAMPLE 5: Example Claims from Taxonomy")
    print("=" * 60)

    for cid in get_cluster_ids():
        examples = get_example_claims(cid)
        counters = get_counter_talking_points(cid)

        print(f"\nCluster: {cid.upper()}")
        print(f"Example priming question:")
        print(f"  {examples[0]}")
        print(f"Counter talking point:")
        print(f"  {counters[0]}")


if __name__ == "__main__":
    example_1_taxonomy_overview()
    example_2_detect_disinformation()
    example_3_generate_priming_questions()
    example_4_counter_messaging()
    example_5_example_claims_by_cluster()
