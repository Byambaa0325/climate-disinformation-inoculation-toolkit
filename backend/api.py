"""
Flask API for the Climate Disinformation Analysis Tool

Provides endpoints for:
- Graph-based disinformation analysis (React + ReactFlow frontend)
- Disinformation detection (rule-based, 5-cluster taxonomy)
- LLM-based disinformation injection (multi-turn priming)
- Counter-messaging generation (prebunking + debunking)
- Dataset exploration (climate disinformation dataset)
- Model evaluation results access

Designed for Google Cloud Run deployment (AWS Bedrock backend).
See research/ for taxonomy and methodology documentation.
"""

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sys
import uuid
import json
import gc
import logging
import traceback
from datetime import datetime
from typing import Any, Optional
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# Module imports (gunicorn + local dev compatible pattern)
# ─────────────────────────────────────────────────────────────────────────────

def _import_module(relative_name, absolute_name):
    try:
        mod = __import__(f".{relative_name}", fromlist=[relative_name], package="backend")
        return mod
    except ImportError:
        pass
    try:
        return __import__(absolute_name)
    except ImportError:
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)
        return __import__(absolute_name)


try:
    from .disinformation_detection import DisinformationDetector
    from .disinformation_injection import DisinformationInjector, PERSONA_ATTRIBUTES, CONTENT_FORMATS
    from .counter_messaging import CounterMessagingModule
    from .claim_taxonomy import TAXONOMY, get_taxonomy_for_ui
except ImportError:
    try:
        from disinformation_detection import DisinformationDetector
        from disinformation_injection import DisinformationInjector, PERSONA_ATTRIBUTES, CONTENT_FORMATS
        from counter_messaging import CounterMessagingModule
        from claim_taxonomy import TAXONOMY, get_taxonomy_for_ui
    except ImportError:
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)
        from disinformation_detection import DisinformationDetector
        from disinformation_injection import DisinformationInjector, PERSONA_ATTRIBUTES, CONTENT_FORMATS
        from counter_messaging import CounterMessagingModule
        from claim_taxonomy import TAXONOMY, get_taxonomy_for_ui

# Security (ported from art-of-biasing-LLM)
try:
    from .security import require_api_key, rate_limit, admin_only, usage_tracker, SecurityConfig
except ImportError:
    try:
        from security import require_api_key, rate_limit, admin_only, usage_tracker, SecurityConfig
    except ImportError:
        print("Warning: Security module not available.")
        def require_api_key(f): return f
        def rate_limit(**kwargs): return lambda f: f
        def admin_only(f): return f
        usage_tracker = None
        SecurityConfig = None

# Bedrock LLM service
try:
    from .bedrock_llm_service import get_bedrock_llm_service
    BEDROCK_LLM_AVAILABLE = True
except ImportError:
    try:
        from bedrock_llm_service import get_bedrock_llm_service
        BEDROCK_LLM_AVAILABLE = True
    except Exception as e:
        BEDROCK_LLM_AVAILABLE = False
        print(f"Bedrock LLM service not available: {e}")

# Model results client
try:
    from .model_results_client import ModelResultsClient
except ImportError:
    try:
        from model_results_client import ModelResultsClient
    except ImportError:
        ModelResultsClient = None

# Dataset client
try:
    from .dataset_client import ClimateDisinfoDatasetClient
except ImportError:
    try:
        from dataset_client import ClimateDisinfoDatasetClient
    except ImportError:
        ClimateDisinfoDatasetClient = None

# Model config
try:
    from .model_config import get_generation_models, get_model_info
except ImportError:
    try:
        from model_config import get_generation_models, get_model_info
    except ImportError:
        def get_generation_models(): return []
        def get_model_info(m): return None

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# JSON sanitization utility (ported from source)
# ─────────────────────────────────────────────────────────────────────────────

def sanitize_for_json(obj: Any) -> Any:
    if obj is None:
        return None
    if isinstance(obj, (bool, int, float, str)):
        return obj
    if isinstance(obj, (list, tuple)):
        return [sanitize_for_json(item) for item in obj]
    if isinstance(obj, dict):
        return {str(k): sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, set):
        return [sanitize_for_json(item) for item in obj]
    if hasattr(obj, "__dict__"):
        return sanitize_for_json(obj.__dict__)
    return str(obj)

# ─────────────────────────────────────────────────────────────────────────────
# Flask app setup
# ─────────────────────────────────────────────────────────────────────────────

FRONTEND_BUILD_DIR = Path(__file__).parent.parent / "frontend-react" / "build"
if not FRONTEND_BUILD_DIR.exists():
    FRONTEND_BUILD_DIR = Path("/app/frontend-react/build")

app = Flask(__name__, static_folder=str(FRONTEND_BUILD_DIR), static_url_path="")
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
    force=True,
)
logger = logging.getLogger("climate-api")

# Singletons
disinfo_detector = DisinformationDetector()
disinfo_injector = DisinformationInjector()  # no LLM initially; injected lazily
counter_module = CounterMessagingModule()

# Dataset client (lazy init — dataset may not exist yet)
_dataset_client = None

def get_dataset_client():
    global _dataset_client
    if _dataset_client is None and ClimateDisinfoDatasetClient:
        try:
            _dataset_client = ClimateDisinfoDatasetClient()
        except FileNotFoundError:
            pass
    return _dataset_client

# Model results client (lazy init)
_results_client = None

def get_results_client():
    global _results_client
    if _results_client is None and ModelResultsClient:
        try:
            _results_client = ModelResultsClient()
        except FileNotFoundError:
            pass
    return _results_client

def get_llm_service(model_id: Optional[str] = None):
    """Get Bedrock LLM service."""
    if not BEDROCK_LLM_AVAILABLE:
        return None
    try:
        return get_bedrock_llm_service()
    except Exception as e:
        logger.error("LLM service init failed: %s\n%s", e, traceback.format_exc())
        return None

# ─────────────────────────────────────────────────────────────────────────────
# Routes: Health & Frontend
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "climate-disinformation",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "llm_available": BEDROCK_LLM_AVAILABLE,
        "taxonomy_clusters": list(TAXONOMY.keys()),
    })

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    if path and (FRONTEND_BUILD_DIR / path).exists():
        return send_from_directory(str(FRONTEND_BUILD_DIR), path)
    index = FRONTEND_BUILD_DIR / "index.html"
    if index.exists():
        return send_file(str(index))
    return jsonify({"message": "Frontend not built. Run: cd frontend-react && npm run build"}), 200

# ─────────────────────────────────────────────────────────────────────────────
# Routes: Taxonomy
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/taxonomy/clusters")
@require_api_key
def get_clusters():
    """Return all 5 clusters with techniques, descriptions, and examples."""
    return jsonify({
        "clusters": get_taxonomy_for_ui(),
        "total_clusters": len(TAXONOMY),
        "framework_sources": ["FLICC (Cook et al., 2022)", "CARDS v2 (Touzel et al., 2023)", "4D Framework"],
    })

@app.route("/api/taxonomy/clusters/<cluster_id>")
@require_api_key
def get_cluster_detail(cluster_id):
    """Return full details for one cluster."""
    if cluster_id not in TAXONOMY:
        return jsonify({"error": f"Unknown cluster '{cluster_id}'"}), 404
    data = TAXONOMY[cluster_id].copy()
    data.pop("patterns", None)  # Don't expose raw regexes
    return jsonify(data)


# ─────────────────────────────────────────────────────────────────────────────
# Routes: Personas (AI-TRAITS methodology, Leite et al. 2025)
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/personas")
@require_api_key
def get_personas():
    """
    Return available persona attributes for targeted disinformation transformation.

    Based on AI-TRAITS methodology (Leite et al., 2025):
    country × generation × political_orientation = 150 unique persona profiles.
    """
    return jsonify({
        "persona_attributes": PERSONA_ATTRIBUTES,
        "total_profiles": (
            len(PERSONA_ATTRIBUTES["country"])
            * len(PERSONA_ATTRIBUTES["generation"])
            * len(PERSONA_ATTRIBUTES["political_orientation"])
        ),
        "reference": "AI-TRAITS: Leite et al. (2025). A Multilingual, Large-Scale Study of the Interplay between LLM Safeguards, Personalisation, and Disinformation.",
    })

# ─────────────────────────────────────────────────────────────────────────────
# Routes: Content formats
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/content-formats")
@require_api_key
def get_content_formats():
    """Return available content output formats for disinformation transformation."""
    return jsonify({"formats": CONTENT_FORMATS})


# ─────────────────────────────────────────────────────────────────────────────
# Routes: Graph (disinformation analysis)
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/transform", methods=["POST"])
@require_api_key
@rate_limit()
def transform_single():
    """
    Transform a single statement for one cluster, with optional persona targeting.

    Request body:
        statement (str): Factual statement to transform
        cluster_id (str): Which cluster technique to apply
        persona (dict, optional): {country, generation, political_orientation}
        use_llm (bool, optional): default True
        generator_model_id (str, optional)

    Returns:
        {transformed_statement, cluster_id, persona}
    """
    data = request.get_json()
    statement = (data.get("statement") or "").strip() if data else ""
    cluster_id = data.get("cluster_id") if data else None
    persona = data.get("persona") or None if data else None
    technique = data.get("technique") or None if data else None
    use_llm = data.get("use_llm", True) if data else True
    generator_model_id = data.get("generator_model_id") if data else None
    content_format = data.get("content_format") or "headline" if data else "headline"

    if not statement:
        return jsonify({"error": "Missing 'statement'"}), 400
    if not cluster_id or cluster_id not in TAXONOMY:
        return jsonify({"error": f"Invalid cluster_id: '{cluster_id}'"}), 400
    if content_format not in CONTENT_FORMATS:
        content_format = "headline"

    if persona:
        for key in ("country", "generation", "political_orientation"):
            val = persona.get(key)
            if val and val not in PERSONA_ATTRIBUTES.get(key, {}):
                return jsonify({"error": f"Invalid persona.{key}: '{val}'"}), 400

    llm_service = get_llm_service() if use_llm else None
    injector = DisinformationInjector(llm_service=llm_service)

    try:
        transformed = injector.transform_statement(
            statement, cluster_id, generator_model_id, persona, technique, content_format
        )
        return jsonify(sanitize_for_json({
            "transformed_statement": transformed,
            "cluster_id": cluster_id,
            "persona": persona,
            "technique": technique,
            "content_format": content_format,
        }))
    except Exception as e:
        logger.error("transform_single failed: %s\n%s", e, traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@app.route("/api/graph/expand", methods=["POST"])
@require_api_key
@rate_limit()
def expand_graph():
    """
    Generate a disinformation transformation graph from a factual climate statement.

    Shows how the statement gets distorted by each of the 5 taxonomy clusters.

    Request body:
        statement (str): Factual climate statement to transform
        use_llm (bool, optional): Use LLM for generation (default: True)
        generator_model_id (str, optional): Model to use for generation

    Returns:
        Graph nodes + edges, one transformed-statement node per cluster + root
    """
    import math

    data = request.get_json()
    statement = (data.get("statement") or data.get("question") or "").strip() if data else ""
    if not statement:
        return jsonify({"error": "Missing 'statement' field"}), 400

    use_llm = data.get("use_llm", True)
    generator_model_id = data.get("generator_model_id")
    content_format = data.get("content_format") or "headline"
    if content_format not in CONTENT_FORMATS:
        content_format = "headline"

    # Transform statement using LLM or rule-based fallback (no persona at this stage)
    llm_service = get_llm_service() if use_llm else None
    injector = DisinformationInjector(llm_service=llm_service)

    try:
        transformations = injector.transform_all_statements(
            statement, generator_model_id, content_format=content_format
        )
    except Exception as e:
        logger.error("transform_all_statements failed: %s\n%s", e, traceback.format_exc())
        transformations = {cid: f"[Transformation failed: {e}]" for cid in TAXONOMY}

    # Build graph nodes
    root_id = f"root_{uuid.uuid4().hex[:8]}"
    nodes = [
        {
            "id": root_id,
            "type": "root",
            "label": statement[:80] + ("..." if len(statement) > 80 else ""),
            "data": {
                "statement": statement,
                "node_type": "root",
            },
            "position": {"x": 0, "y": 0},
            "style": {"background": "#2E7D32", "color": "white"},
        }
    ]

    cluster_colors = {
        "denial": "#D32F2F",
        "doubt_casting": "#F57C00",
        "deflection": "#7B1FA2",
        "delay": "#0288D1",
        "conspiracy": "#5D4037",
    }

    edges = []
    for i, (cluster_id, transformed) in enumerate(transformations.items()):
        cluster_data = TAXONOMY[cluster_id]
        node_id = f"{cluster_id}_{uuid.uuid4().hex[:8]}"

        angle = (i / len(TAXONOMY)) * 360
        x = int(350 * math.cos(math.radians(angle)))
        y = int(350 * math.sin(math.radians(angle)))

        nodes.append({
            "id": node_id,
            "type": "disinformed",
            "label": cluster_data["display_name"],
            "data": {
                "cluster_id": cluster_id,
                "display_name": cluster_data["display_name"],
                "description": cluster_data["description"],
                "original_statement": statement,
                "transformed_statement": transformed,
                "techniques": cluster_data["techniques"],
                "counter_points": cluster_data["counter_talking_points"],
                "node_type": "disinformed",
            },
            "position": {"x": x, "y": y},
            "style": {"background": cluster_colors.get(cluster_id, "#666"), "color": "white"},
        })

        edges.append({
            "id": f"edge_{root_id}_{node_id}",
            "source": root_id,
            "target": node_id,
            "label": cluster_data["display_name"],
            "data": {"cluster": cluster_id},
        })

    gc.collect()
    return jsonify(sanitize_for_json({
        "nodes": nodes,
        "edges": edges,
        "transformations": transformations,
    }))


@app.route("/api/graph/expand-node", methods=["POST"])
@require_api_key
@rate_limit()
def expand_node():
    """
    Expand a specific graph node by running the multi-turn evaluation.

    Request body:
        node_id (str): The node to expand
        cluster_id (str): Disinformation cluster
        target_question (str): The climate science question
        model_id (str, optional): Target evaluation model
        action (str): 'evaluate' | 'counter'

    Returns:
        Evaluation results or counter-messaging for the node
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing request body"}), 400

    cluster_id = data.get("cluster_id")
    target_question = data.get("target_question")
    action = data.get("action", "evaluate")
    model_id = data.get("model_id")

    if not cluster_id or cluster_id not in TAXONOMY:
        return jsonify({"error": f"Invalid cluster_id: {cluster_id}"}), 400

    if action == "counter":
        prebunk = counter_module.generate_prebunking(cluster_id, target_question)
        return jsonify(sanitize_for_json({
            "action": "counter",
            "cluster_id": cluster_id,
            "prebunking": prebunk,
        }))

    # action == "evaluate": run multi-turn with LLM
    llm_service = get_llm_service()
    if not llm_service:
        return jsonify({"error": "LLM service not available. Configure .env.bedrock"}), 503

    try:
        injector = DisinformationInjector(llm_service=llm_service)
        result = injector.inject_disinformation(
            target_question=target_question,
            cluster_id=cluster_id,
            model_id=model_id,
        )

        # Detect disinformation in the primed response
        primed_detection = disinfo_detector.detect(result["turn2_response"])
        control_detection = disinfo_detector.detect(result["control_response"])

        result["primed_detection"] = primed_detection
        result["control_detection"] = control_detection
        result["drift_indicator"] = (
            primed_detection["overall_score"] - control_detection["overall_score"]
        )

        return jsonify(sanitize_for_json(result))
    except Exception as e:
        logger.error("expand_node failed: %s\n%s", e, traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@app.route("/api/graph/evaluate", methods=["POST"])
@require_api_key
@rate_limit()
def evaluate_response():
    """
    Evaluate an LLM response for disinformation signals.

    Request body:
        response (str): LLM response text to evaluate
        cluster_id (str, optional): Expected cluster for context

    Returns:
        Detection results with cluster scores and severity
    """
    data = request.get_json()
    if not data or not data.get("response"):
        return jsonify({"error": "Missing 'response' field"}), 400

    response_text = data["response"]
    result = disinfo_detector.detect(response_text)

    return jsonify(sanitize_for_json({
        "detection": result,
        "explanation": disinfo_detector.get_explanation(result["primary_cluster"])
        if result["primary_cluster"] else "No disinformation signals detected.",
    }))

# ─────────────────────────────────────────────────────────────────────────────
# Routes: Models
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/models")
@require_api_key
def get_models():
    """Return available generation models."""
    return jsonify({
        "generation_models": get_generation_models(),
        "llm_available": BEDROCK_LLM_AVAILABLE,
    })

# ─────────────────────────────────────────────────────────────────────────────
# Routes: News Headlines
# ─────────────────────────────────────────────────────────────────────────────

_NEWS_FILE = Path(__file__).parent.parent / "data" / "news_headlines.json"

@app.route("/api/news/headlines")
@require_api_key
def news_headlines():
    """
    Return climate news headlines from data/news_headlines.json.

    Query params:
        source (str, optional): Filter by source name
        q (str, optional): Substring search in title/description
        page (int, default=0)
        page_size (int, default=20)
    """
    if not _NEWS_FILE.exists():
        return jsonify({"headlines": [], "total": 0,
                        "message": "No headlines found. Run: python scripts/fetch_news.py"})

    with open(_NEWS_FILE, "r", encoding="utf-8") as f:
        all_headlines = json.load(f)

    source_filter = request.args.get("source", "").strip().lower()
    q = request.args.get("q", "").strip().lower()
    page = int(request.args.get("page", 0))
    page_size = min(int(request.args.get("page_size", 20)), 100)

    filtered = all_headlines
    if source_filter:
        filtered = [h for h in filtered if source_filter in h.get("source", "").lower()]
    if q:
        filtered = [h for h in filtered
                    if q in h.get("title", "").lower() or q in h.get("description", "").lower()]

    total = len(filtered)
    page_items = filtered[page * page_size: (page + 1) * page_size]

    sources = sorted({h.get("source", "") for h in all_headlines if h.get("source")})

    return jsonify({
        "headlines": page_items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "sources": sources,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Routes: Dataset
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/dataset/stats")
@require_api_key
def dataset_stats():
    """Return dataset statistics."""
    client = get_dataset_client()
    if not client:
        return jsonify({
            "status": "empty",
            "message": "Dataset not yet generated. Run notebooks/05_prompt_engineering.ipynb.",
            "total_entries": 0,
        })
    return jsonify(sanitize_for_json(client.get_stats()))


@app.route("/api/dataset/entries")
@require_api_key
def dataset_entries():
    """
    Return paginated dataset entries.

    Query params:
        topic_area (str, optional)
        cluster (str, optional)
        page (int, default=0)
        page_size (int, default=10)
    """
    client = get_dataset_client()
    if not client:
        return jsonify({"entries": [], "total": 0, "message": "Dataset not available."})

    topic_area = request.args.get("topic_area")
    cluster = request.args.get("cluster")
    page = int(request.args.get("page", 0))
    page_size = int(request.args.get("page_size", 10))

    try:
        result = client.get_entries(
            topic_area=topic_area,
            cluster=cluster,
            page=page,
            page_size=page_size,
        )
        return jsonify(sanitize_for_json(result))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/dataset/entries/<int:index>")
@require_api_key
def dataset_entry(index):
    """Get a single dataset entry by index."""
    client = get_dataset_client()
    if not client:
        return jsonify({"error": "Dataset not available"}), 404
    try:
        entry = client.get_entry(index)
        return jsonify(sanitize_for_json(entry))
    except IndexError as e:
        return jsonify({"error": str(e)}), 404

# ─────────────────────────────────────────────────────────────────────────────
# Routes: Model Results (pre-computed evaluations)
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/results/<model_id>/<int:entry_index>")
@require_api_key
def get_results(model_id, entry_index):
    """Get pre-computed evaluation results for a model + entry."""
    client = get_results_client()
    if not client:
        return jsonify({"error": "Results not available"}), 404
    try:
        result = client.get_result_by_index(model_id, entry_index)
        return jsonify(sanitize_for_json(result))
    except (ValueError, Exception) as e:
        return jsonify({"error": str(e)}), 404

# ─────────────────────────────────────────────────────────────────────────────
# Routes: Counter-Messaging
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/counter/prebunking/<cluster_id>")
@require_api_key
def prebunking(cluster_id):
    """Get prebunking message for a cluster."""
    if cluster_id not in TAXONOMY:
        return jsonify({"error": f"Unknown cluster '{cluster_id}'"}), 404
    result = counter_module.generate_prebunking(cluster_id)
    return jsonify(sanitize_for_json(result))


@app.route("/api/counter/debunking", methods=["POST"])
@require_api_key
@rate_limit()
def debunking():
    """
    Generate a debunking response for a specific claim.

    Request body:
        claim (str): The disinformation claim to debunk
        cluster_id (str): Which cluster the claim belongs to
        accurate_info (str, optional): Ground-truth accurate information
    """
    data = request.get_json()
    if not data or not data.get("claim") or not data.get("cluster_id"):
        return jsonify({"error": "Missing 'claim' or 'cluster_id'"}), 400

    cluster_id = data["cluster_id"]
    if cluster_id not in TAXONOMY:
        return jsonify({"error": f"Unknown cluster '{cluster_id}'"}), 400

    result = counter_module.generate_debunking(
        claim=data["claim"],
        cluster_id=cluster_id,
        accurate_info=data.get("accurate_info"),
    )
    return jsonify(sanitize_for_json(result))


# ─────────────────────────────────────────────────────────────────────────────
# Error handlers
# ─────────────────────────────────────────────────────────────────────────────

@app.errorhandler(Exception)
def handle_unhandled_exception(e):
    logger.error("Unhandled exception on %s %s:\n%s",
                 request.method, request.path, traceback.format_exc())
    return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    print(f"Starting Climate Disinformation API on port {port}")
    print(f"Taxonomy: {len(TAXONOMY)} clusters loaded")
    print(f"LLM (Bedrock): {'available' if BEDROCK_LLM_AVAILABLE else 'not configured'}")
    app.run(host="0.0.0.0", port=port, debug=debug)
