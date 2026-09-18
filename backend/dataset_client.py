"""
Climate Disinformation Dataset Client

Provides access to the climate disinformation multi-turn dataset.
Multi-turn dataset schema organised by the 5-cluster unified climate
disinformation taxonomy.

Dataset location: data/climate_disinfo_dataset.json
"""

import json
import os
import random
from typing import List, Dict, Optional, Any
from pathlib import Path


class ClimateDisinfoDatasetClient:
    """
    Client for the climate disinformation multi-turn dataset.

    Dataset schema (per entry):
    {
        "entry_index": 0,
        "target_question": "What does scientific evidence show about...",
        "topic_area": "temperature_trends",
        "primary_cluster": "denial",
        "source_framework": "FLICC",
        "ipcc_reference": "AR6 WGI Chapter 2",
        "accurate_answer_summary": "Global temperatures have risen 1.1°C...",

        # Pre-generated Turn 1 priming questions (one per cluster)
        "turn1_question_denial": "...",
        "turn1_question_doubt_casting": "...",
        "turn1_question_deflection": "...",
        "turn1_question_delay": "...",
        "turn1_question_conspiracy": "...",

        # Metadata
        "generator_model": "us.amazon.nova-pro-v1:0",
        "generation_timestamp": "2025-01-01T00:00:00Z"
    }
    """

    VALID_CLUSTERS = ["denial", "doubt_casting", "deflection", "delay", "conspiracy"]

    VALID_TOPIC_AREAS = [
        "temperature_trends",
        "sea_level_rise",
        "ice_and_arctic",
        "extreme_weather",
        "ocean_acidification",
        "emission_sources",
        "climate_modelling",
        "ecosystem_impacts",
        "human_society_impacts",
        "mitigation_adaptation",
    ]

    def __init__(self, dataset_path: Optional[str] = None):
        """
        Args:
            dataset_path: Path to climate_disinfo_dataset.json.
                          Defaults to data/climate_disinfo_dataset.json
                          relative to the project root.
        """
        if dataset_path is None:
            current_dir = Path(__file__).parent
            dataset_path = current_dir.parent / "data" / "climate_disinfo_dataset.json"

        self.dataset_path = Path(dataset_path)

        if not self.dataset_path.exists():
            raise FileNotFoundError(
                f"Dataset not found at {self.dataset_path}."
            )

        self._load()

    def _load(self):
        with open(self.dataset_path, "r", encoding="utf-8") as f:
            self.entries: List[Dict[str, Any]] = json.load(f)

        if not self.entries:
            self.entries = []

    # ──────────────────────────────────────────────────────────────────────────
    # Access methods
    # ──────────────────────────────────────────────────────────────────────────

    def __len__(self) -> int:
        return len(self.entries)

    def get_entry(self, index: int) -> Dict[str, Any]:
        """Get a single entry by index."""
        if index < 0 or index >= len(self.entries):
            raise IndexError(f"Entry index {index} out of range (0-{len(self.entries)-1})")
        return self.entries[index]

    def get_entries(
        self,
        topic_area: Optional[str] = None,
        cluster: Optional[str] = None,
        page: int = 0,
        page_size: int = 10,
    ) -> Dict[str, Any]:
        """
        Get paginated entries with optional filtering.

        Args:
            topic_area: Filter by topic area (see VALID_TOPIC_AREAS)
            cluster: Filter by primary_cluster
            page: Page number (0-indexed)
            page_size: Entries per page (5, 10, 25, or 50)

        Returns:
            Dict with entries, total, page info
        """
        filtered = self.entries

        if topic_area:
            filtered = [e for e in filtered if e.get("topic_area") == topic_area]

        if cluster:
            if cluster not in self.VALID_CLUSTERS:
                raise ValueError(
                    f"Invalid cluster '{cluster}'. "
                    f"Valid: {self.VALID_CLUSTERS}"
                )
            filtered = [e for e in filtered if e.get("primary_cluster") == cluster]

        total = len(filtered)
        start = page * page_size
        end = start + page_size
        page_entries = filtered[start:end]

        return {
            "entries": page_entries,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": max(1, (total + page_size - 1) // page_size),
        }

    def get_random_entry(
        self,
        topic_area: Optional[str] = None,
        cluster: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get a random entry, optionally filtered."""
        pool = self.entries

        if topic_area:
            pool = [e for e in pool if e.get("topic_area") == topic_area]
        if cluster:
            pool = [e for e in pool if e.get("primary_cluster") == cluster]

        if not pool:
            raise ValueError("No entries match the given filters.")

        return random.choice(pool)

    def get_stats(self) -> Dict[str, Any]:
        """Return dataset statistics."""
        if not self.entries:
            return {
                "total_entries": 0,
                "status": "empty",
            }

        cluster_counts: Dict[str, int] = {}
        topic_counts: Dict[str, int] = {}

        for entry in self.entries:
            c = entry.get("primary_cluster", "unknown")
            t = entry.get("topic_area", "unknown")
            cluster_counts[c] = cluster_counts.get(c, 0) + 1
            topic_counts[t] = topic_counts.get(t, 0) + 1

        return {
            "total_entries": len(self.entries),
            "cluster_distribution": cluster_counts,
            "topic_distribution": topic_counts,
            "valid_clusters": self.VALID_CLUSTERS,
            "valid_topic_areas": self.VALID_TOPIC_AREAS,
        }


def get_dataset_client(dataset_path: Optional[str] = None) -> ClimateDisinfoDatasetClient:
    """Get or create a dataset client instance."""
    return ClimateDisinfoDatasetClient(dataset_path)


if __name__ == "__main__":
    try:
        client = ClimateDisinfoDatasetClient()
        stats = client.get_stats()
        print(f"Dataset loaded: {stats['total_entries']} entries")
    except FileNotFoundError as e:
        print(f"Dataset not yet generated: {e}")
