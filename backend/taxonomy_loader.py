"""
Load rich taxonomy from data/unified_taxonomy.json for use in prompts.

Provides cluster and technique descriptions, example claims, and source
framework labels so prompts can be enhanced with authoritative technique
definitions from the unified schema (FLICC, CARDS, 4D).
"""

from pathlib import Path
from typing import Dict, Any, List, Optional

_TAXONOMY_DATA: Optional[Dict[str, Any]] = None  # cluster_id -> rich cluster dict


def _taxonomy_path() -> Path:
    """Path to data/unified_taxonomy.json from repo root."""
    backend_dir = Path(__file__).resolve().parent
    root = backend_dir.parent
    return root / "data" / "unified_taxonomy.json"


def _load() -> Dict[str, Dict[str, Any]]:
    """Load taxonomy once; return dict cluster_id -> cluster data with techniques list."""
    global _TAXONOMY_DATA
    if _TAXONOMY_DATA is not None:
        return _TAXONOMY_DATA
    path = _taxonomy_path()
    if not path.exists():
        _TAXONOMY_DATA = {}
        return _TAXONOMY_DATA
    import json
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    clusters = data.get("clusters", [])
    _TAXONOMY_DATA = {c["id"]: c for c in clusters}
    return _TAXONOMY_DATA


def get_rich_cluster(cluster_id: str) -> Optional[Dict[str, Any]]:
    """Return full cluster dict with techniques (each with id, name, description, example_claim, etc.)."""
    data = _load()
    return data.get(cluster_id)


def get_technique_info(cluster_id: str, technique_id: str) -> Optional[Dict[str, Any]]:
    """Return technique dict (name, description, example_claim, counter_talking_point, source) or None."""
    cluster = get_rich_cluster(cluster_id)
    if not cluster:
        return None
    for t in cluster.get("techniques", []):
        if t.get("id") == technique_id:
            return t
    return None


def format_technique_guidance_for_prompt(cluster_id: str) -> str:
    """Format all techniques for this cluster as a single block for injection/transformation prompts."""
    cluster = get_rich_cluster(cluster_id)
    if not cluster:
        return ""
    lines = []
    for t in cluster.get("techniques", []):
        name = t.get("name", t.get("id", "").replace("_", " ").title())
        desc = t.get("description", "")
        example = t.get("example_claim", "")
        part = f"- {name}: {desc}"
        if example:
            part += f" Example: \"{example}\""
        lines.append(part)
    return "\n".join(lines) if lines else ""


def get_cluster_description(cluster_id: str) -> str:
    """Return the cluster's main description text."""
    cluster = get_rich_cluster(cluster_id)
    if not cluster:
        return ""
    return cluster.get("description", "")


def get_source_frameworks(cluster_id: str) -> List[str]:
    """Return list of source framework labels for this cluster."""
    cluster = get_rich_cluster(cluster_id)
    if not cluster:
        return []
    return cluster.get("source_frameworks", [])
