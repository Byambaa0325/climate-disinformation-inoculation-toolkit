"""
API Helper Functions

Extracts common patterns from api.py to reduce code duplication:
- Request validation
- Node building
- Response formatting
- Error handling
"""

from typing import Any, Dict, List, Optional, Tuple
from functools import wraps
from flask import request, jsonify
import uuid


def sanitize_for_json(obj: Any) -> Any:
    """
    Recursively convert any object to JSON-serializable primitives.

    Args:
        obj: Any Python object

    Returns:
        JSON-serializable version of the object
    """
    if obj is None:
        return None

    if isinstance(obj, (bool, int, float, str)):
        return obj

    if isinstance(obj, (list, tuple)):
        return [sanitize_for_json(item) for item in obj]

    if isinstance(obj, dict):
        return {str(key): sanitize_for_json(value) for key, value in obj.items()}

    if isinstance(obj, set):
        return [sanitize_for_json(item) for item in obj]

    if hasattr(obj, '__dict__'):
        return sanitize_for_json(obj.__dict__)

    return str(obj)


def validate_json_request(*required_fields: str):
    """
    Decorator to validate JSON request body.

    Args:
        *required_fields: Field names that must be present and non-empty

    Usage:
        @validate_json_request('prompt')
        def my_endpoint():
            data = request.get_json()
            # data is guaranteed to have 'prompt'
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No JSON data provided'}), 400

            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'No {field} provided'}), 400

            return f(*args, **kwargs)
        return wrapper
    return decorator


def build_node_from_detection(
    node_id: str,
    prompt: str,
    llm_answer: str,
    detected_biases: Dict[str, Any],
    node_type: str = 'original',
    use_hearts: bool = False,
    parent_id: Optional[str] = None,
    transformation: Optional[str] = None,
    transformation_details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Build a graph node from bias detection results.

    Args:
        node_id: Unique identifier for the node
        prompt: The prompt text
        llm_answer: LLM-generated answer
        detected_biases: Results from bias detection
        node_type: Type of node ('original', 'biased', 'debiased')
        use_hearts: Whether HEARTS detection was used
        parent_id: Parent node ID (for child nodes)
        transformation: Transformation label
        transformation_details: Details about the transformation

    Returns:
        Node dictionary ready for JSON response
    """
    # Extract data safely
    hearts_data = detected_biases.get('hearts', {})
    if not isinstance(hearts_data, dict):
        hearts_data = {}

    gemini_data = detected_biases.get('gemini_validation', {})
    if not isinstance(gemini_data, dict):
        gemini_data = {}

    explanations = detected_biases.get('explanations', {})
    if not isinstance(explanations, dict):
        explanations = {}

    # Build token importance safely
    token_importance = []
    if use_hearts and explanations.get('most_biased_tokens'):
        raw_tokens = explanations.get('most_biased_tokens', [])[:10]
        for token in raw_tokens:
            if isinstance(token, dict):
                token_importance.append({
                    'token': str(token.get('token', '')),
                    'importance': float(token.get('importance', 0)),
                    'contribution': str(token.get('contribution', 'unknown')),
                    'source': str(token.get('source', 'HEARTS-SHAP'))
                })

    node = {
        'id': node_id,
        'prompt': prompt,
        'llm_answer': llm_answer,
        'type': node_type,

        # HEARTS ML evaluation
        'hearts_evaluation': {
            'available': use_hearts,
            'is_stereotype': bool(hearts_data.get('is_stereotype', False)) if use_hearts else None,
            'confidence': float(hearts_data.get('confidence', 0)) if use_hearts else None,
            'probabilities': dict(hearts_data.get('probabilities', {})) if use_hearts else {},
            'prediction': str(hearts_data.get('prediction', 'Unknown')) if use_hearts else None,
            'token_importance': token_importance,
            'model': 'HEARTS ALBERT-v2' if use_hearts else None
        },

        # Gemini LLM evaluation
        'gemini_evaluation': {
            'available': bool(gemini_data),
            'bias_score': float(gemini_data.get('evaluation', {}).get('bias_score', 0)) if gemini_data else None,
            'severity': str(gemini_data.get('evaluation', {}).get('severity', 'unknown')) if gemini_data else None,
            'bias_types': list(gemini_data.get('evaluation', {}).get('bias_types', [])) if gemini_data else [],
            'explanation': str(gemini_data.get('evaluation', {}).get('explanation', '')) if gemini_data else None,
            'recommendations': str(gemini_data.get('evaluation', {}).get('recommendations', '')) if gemini_data else None,
            'model': 'Gemini 2.5 Flash' if gemini_data else None
        },

        # Bias metrics from individual judges
        'bias_metrics': detected_biases.get('bias_metrics', []),
        'judge_count': detected_biases.get('judge_count', 0),
        'judges_used': detected_biases.get('judges_used', []),

        # Overall metrics
        'bias_score': float(detected_biases.get('overall_bias_score', 0)),
        'confidence': float(detected_biases.get('confidence', 0)),
        'source_agreement': float(detected_biases.get('source_agreement', 1.0)),

        # Metadata
        'detection_sources': list(detected_biases.get('detection_sources', ['Rule-based'])),
        'layers_used': list(detected_biases.get('layers_used', ['rule-based'])),
        'frameworks': list(explanations.get('frameworks', []))
    }

    # Add parent/transformation info for child nodes
    if parent_id:
        node['parent_id'] = parent_id
    if transformation:
        node['transformation'] = transformation
    if transformation_details:
        node['transformation_details'] = transformation_details

    return node


def build_potential_paths(
    node_id: str,
    available_biases: List[Dict[str, Any]],
    available_debiases: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Build potential path edges from available bias/debias options.

    Args:
        node_id: Source node ID
        available_biases: List of available bias types
        available_debiases: List of available debias methods

    Returns:
        List of edge dictionaries (without targets)
    """
    edges = []

    # Add bias paths
    for bias_option in available_biases:
        edges.append({
            'id': f"{node_id}-bias-{bias_option['bias_type']}",
            'source': node_id,
            'type': 'bias',
            'bias_type': bias_option['bias_type'],
            'label': bias_option['label'],
            'description': bias_option['description'],
            'severity': bias_option.get('severity', 'medium'),
            'action_required': 'click_to_generate'
        })

    # Add debias paths
    for debias_option in available_debiases:
        edges.append({
            'id': f"{node_id}-debias-{debias_option['method']}",
            'source': node_id,
            'type': 'debias',
            'method': debias_option['method'],
            'label': debias_option['label'],
            'description': debias_option['description'],
            'effectiveness': debias_option.get('effectiveness', 'high'),
            'action_required': 'click_to_generate'
        })

    return edges


def build_connecting_edge(
    parent_id: str,
    new_id: str,
    action: str,
    label: str
) -> Dict[str, Any]:
    """
    Build a connecting edge between parent and child nodes.

    Args:
        parent_id: Parent node ID
        new_id: Child node ID
        action: Action type ('bias' or 'debias')
        label: Edge label

    Returns:
        Edge dictionary
    """
    return {
        'id': f"{parent_id}-{new_id}",
        'source': parent_id,
        'target': new_id,
        'type': action,
        'label': label,
        'transformation': action
    }


def generate_node_id() -> str:
    """Generate a unique node ID."""
    return str(uuid.uuid4())


def api_error_handler(f):
    """
    Decorator for consistent API error handling.

    Catches exceptions and returns formatted error responses.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            import traceback
            print(f"Error in {f.__name__}: {e}")
            traceback.print_exc()
            return jsonify({'error': f'{f.__name__} failed: {str(e)}'}), 500
    return wrapper


class APIResponse:
    """Helper class for building consistent API responses."""

    @staticmethod
    def success(data: Dict[str, Any]) -> Tuple[Any, int]:
        """Return success response."""
        return jsonify(sanitize_for_json(data)), 200

    @staticmethod
    def error(message: str, status_code: int = 400) -> Tuple[Any, int]:
        """Return error response."""
        return jsonify({'error': message}), status_code

    @staticmethod
    def not_available(service: str) -> Tuple[Any, int]:
        """Return service not available response."""
        return jsonify({'error': f'{service} not available'}), 503
