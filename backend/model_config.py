"""
Model Configuration for Vertex AI

Defines available models from different providers accessible through Vertex AI:
- Meta (Llama models)
- Anthropic (Claude models)
- Mistral AI
- OpenAI (via Vertex AI)
- Qwen (Alibaba)
"""

from typing import Dict, List, Any

# Model categories
MODEL_CATEGORIES = {
    'generation': 'Text Generation',
    'evaluation': 'Bias Evaluation',
    'both': 'Generation & Evaluation'
}

# Available models through Vertex AI
AVAILABLE_MODELS = {
    # Meta Llama 3.3 Models
    'meta/llama-3.3-70b-instruct-maas': {
        'name': 'Llama 3.3 70B',
        'provider': 'Meta',
        'category': 'both',
        'description': 'Latest Llama 3.3, excellent for reasoning and instruction following',
        'context_window': 128000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'openapi'
    },

    # Meta Llama 3.1 Models
    'meta/llama-3.1-405b-instruct-maas': {
        'name': 'Llama 3.1 405B',
        'provider': 'Meta',
        'category': 'both',
        'description': 'Largest Llama 3.1 model, exceptional performance',
        'context_window': 128000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'openapi'
    },
    'meta/llama-3.1-70b-instruct-maas': {
        'name': 'Llama 3.1 70B',
        'provider': 'Meta',
        'category': 'both',
        'description': 'Balanced Llama 3.1, good performance and speed',
        'context_window': 128000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'openapi'
    },

    # Google Gemini Models (for comparison)
    'gemini-2.0-flash-exp': {
        'name': 'Gemini 2.0 Flash',
        'provider': 'Google',
        'category': 'both',
        'description': 'Latest Gemini flash model, fast and capable',
        'context_window': 1000000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'vertex_sdk'
    },
    'gemini-1.5-pro-002': {
        'name': 'Gemini 1.5 Pro',
        'provider': 'Google',
        'category': 'both',
        'description': 'Google\'s Pro model with extended context',
        'context_window': 2000000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'vertex_sdk'
    },
    'gemini-1.5-flash-002': {
        'name': 'Gemini 1.5 Flash',
        'provider': 'Google',
        'category': 'both',
        'description': 'Fast Gemini model for quick tasks',
        'context_window': 1000000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'vertex_sdk'
    },

    # AWS Bedrock - Anthropic Claude Series
    'us.anthropic.claude-3-5-sonnet-20241022-v2:0': {
        'name': 'Claude 3.5 Sonnet v2',
        'provider': 'Anthropic (Bedrock)',
        'category': 'both',
        'description': 'Latest Claude 3.5 Sonnet, excellent for reasoning and evaluation',
        'context_window': 200000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'bedrock'
    },
    'us.anthropic.claude-3-5-haiku-20241022-v1:0': {
        'name': 'Claude 3.5 Haiku',
        'provider': 'Anthropic (Bedrock)',
        'category': 'both',
        'description': 'Fast Claude 3.5 model, great for quick tasks',
        'context_window': 200000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'bedrock'
    },
    'us.anthropic.claude-3-opus-20240229-v1:0': {
        'name': 'Claude 3 Opus',
        'provider': 'Anthropic (Bedrock)',
        'category': 'both',
        'description': 'Most capable Claude 3 model',
        'context_window': 200000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'bedrock'
    },
    'us.anthropic.claude-3-sonnet-20240229-v1:0': {
        'name': 'Claude 3 Sonnet',
        'provider': 'Anthropic (Bedrock)',
        'category': 'both',
        'description': 'Balanced Claude 3 model',
        'context_window': 200000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'bedrock'
    },
    'us.anthropic.claude-3-haiku-20240307-v1:0': {
        'name': 'Claude 3 Haiku',
        'provider': 'Anthropic (Bedrock)',
        'category': 'both',
        'description': 'Fast Claude 3 model',
        'context_window': 200000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'bedrock'
    },
    'us.anthropic.claude-opus-4-20250514-v1:0': {
        'name': 'Claude Opus 4',
        'provider': 'Anthropic (Bedrock)',
        'category': 'both',
        'description': 'Latest Claude Opus 4 model',
        'context_window': 200000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'bedrock'
    },
    'us.anthropic.claude-sonnet-4-20250514-v1:0': {
        'name': 'Claude Sonnet 4',
        'provider': 'Anthropic (Bedrock)',
        'category': 'both',
        'description': 'Latest Claude Sonnet 4 model',
        'context_window': 200000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'bedrock'
    },
    'us.anthropic.claude-sonnet-4-5-20250929-v1:0': {
        'name': 'Claude Sonnet 4.5',
        'provider': 'Anthropic (Bedrock)',
        'category': 'both',
        'description': 'Latest Claude Sonnet 4.5 model',
        'context_window': 200000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'bedrock'
    },
    'us.anthropic.claude-haiku-4-5-20251001-v1:0': {
        'name': 'Claude Haiku 4.5',
        'provider': 'Anthropic (Bedrock)',
        'category': 'both',
        'description': 'Latest Claude Haiku 4.5 model',
        'context_window': 200000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'bedrock'
    },

    # AWS Bedrock - Meta Llama Series
    'us.meta.llama3-2-90b-instruct-v1:0': {
        'name': 'Llama 3.2 90B',
        'provider': 'Meta (Bedrock)',
        'category': 'both',
        'description': 'Large Llama 3.2 model',
        'context_window': 128000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'bedrock'
    },
    'us.meta.llama3-2-11b-instruct-v1:0': {
        'name': 'Llama 3.2 11B',
        'provider': 'Meta (Bedrock)',
        'category': 'both',
        'description': 'Medium Llama 3.2 model',
        'context_window': 128000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'bedrock'
    },
    'us.meta.llama3-2-3b-instruct-v1:0': {
        'name': 'Llama 3.2 3B',
        'provider': 'Meta (Bedrock)',
        'category': 'both',
        'description': 'Small Llama 3.2 model',
        'context_window': 128000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'bedrock'
    },
    'us.meta.llama3-2-1b-instruct-v1:0': {
        'name': 'Llama 3.2 1B',
        'provider': 'Meta (Bedrock)',
        'category': 'both',
        'description': 'Tiny Llama 3.2 model',
        'context_window': 128000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'bedrock'
    },
    'us.meta.llama3-1-70b-instruct-v1:0': {
        'name': 'Llama 3.1 70B',
        'provider': 'Meta (Bedrock)',
        'category': 'both',
        'description': 'Llama 3.1 70B model',
        'context_window': 128000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'bedrock'
    },
    'us.meta.llama3-1-8b-instruct-v1:0': {
        'name': 'Llama 3.1 8B',
        'provider': 'Meta (Bedrock)',
        'category': 'both',
        'description': 'Llama 3.1 8B model',
        'context_window': 128000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'bedrock'
    },
    'us.meta.llama3-3-70b-instruct-v1:0': {
        'name': 'Llama 3.3 70B',
        'provider': 'Meta (Bedrock)',
        'category': 'both',
        'description': 'Latest Llama 3.3 70B model',
        'context_window': 128000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'bedrock'
    },
    'us.meta.llama4-scout-17b-instruct-v1:0': {
        'name': 'Llama 4 Scout 17B',
        'provider': 'Meta (Bedrock)',
        'category': 'both',
        'description': 'Llama 4 Scout model',
        'context_window': 128000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'bedrock'
    },
    'us.meta.llama4-maverick-17b-instruct-v1:0': {
        'name': 'Llama 4 Maverick 17B',
        'provider': 'Meta (Bedrock)',
        'category': 'both',
        'description': 'Llama 4 Maverick model',
        'context_window': 128000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'bedrock'
    },

    # AWS Bedrock - Amazon Nova Series
    'us.amazon.nova-premier-v1:0': {
        'name': 'Nova Premier',
        'provider': 'Amazon (Bedrock)',
        'category': 'both',
        'description': 'Amazon\'s premier model',
        'context_window': 128000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'bedrock'
    },
    'us.amazon.nova-pro-v1:0': {
        'name': 'Nova Pro',
        'provider': 'Amazon (Bedrock)',
        'category': 'both',
        'description': 'Amazon\'s pro model',
        'context_window': 128000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'bedrock'
    },
    'us.amazon.nova-lite-v1:0': {
        'name': 'Nova Lite',
        'provider': 'Amazon (Bedrock)',
        'category': 'both',
        'description': 'Amazon\'s lite model',
        'context_window': 128000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'bedrock'
    },
    'us.amazon.nova-micro-v1:0': {
        'name': 'Nova Micro',
        'provider': 'Amazon (Bedrock)',
        'category': 'both',
        'description': 'Amazon\'s micro model',
        'context_window': 128000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'bedrock'
    },

    # AWS Bedrock - Mistral Series
    'us.mistral.pixtral-large-2502-v1:0': {
        'name': 'Pixtral Large',
        'provider': 'Mistral (Bedrock)',
        'category': 'both',
        'description': 'Mistral\'s large vision model',
        'context_window': 128000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'bedrock'
    },
    'mistral.mistral-large-2402-v1:0': {
        'name': 'Mistral Large',
        'provider': 'Mistral (Bedrock)',
        'category': 'both',
        'description': 'Mistral\'s large model',
        'context_window': 128000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'bedrock'
    },
    'mistral.mistral-small-2402-v1:0': {
        'name': 'Mistral Small',
        'provider': 'Mistral (Bedrock)',
        'category': 'both',
        'description': 'Mistral\'s small model',
        'context_window': 128000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'bedrock'
    },
    'mistral.mistral-7b-instruct-v0:2': {
        'name': 'Mistral 7B',
        'provider': 'Mistral (Bedrock)',
        'category': 'both',
        'description': 'Mistral 7B model',
        'context_window': 128000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'bedrock'
    },
    'mistral.mixtral-8x7b-instruct-v0:1': {
        'name': 'Mixtral 8x7B',
        'provider': 'Mistral (Bedrock)',
        'category': 'both',
        'description': 'Mixtral 8x7B model',
        'context_window': 128000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'bedrock'
    },

    # AWS Bedrock - DeepSeek Series
    'us.deepseek.r1-v1:0': {
        'name': 'DeepSeek R1',
        'provider': 'DeepSeek (Bedrock)',
        'category': 'both',
        'description': 'DeepSeek R1 reasoning model',
        'context_window': 128000,
        'recommended_for': ['generation', 'evaluation'],
        'endpoint_type': 'bedrock'
    },
}

# Default models for each purpose
DEFAULT_MODELS = {
    'generation': 'meta/llama-3.3-70b-instruct-maas',
    'evaluation': 'gemini-2.0-flash-exp'
}


def get_available_models(category: str = None) -> Dict[str, Any]:
    """
    Get available models, optionally filtered by category.

    Args:
        category: Optional category filter ('generation', 'evaluation', 'both')

    Returns:
        Dictionary of available models
    """
    if category:
        return {
            model_id: config
            for model_id, config in AVAILABLE_MODELS.items()
            if category in config['recommended_for'] or config['category'] == 'both'
        }
    return AVAILABLE_MODELS


def get_models_by_provider(provider: str) -> Dict[str, Any]:
    """
    Get models from a specific provider.

    Args:
        provider: Provider name (e.g., 'Meta', 'Anthropic', 'Mistral AI', 'Google')

    Returns:
        Dictionary of models from the provider
    """
    return {
        model_id: config
        for model_id, config in AVAILABLE_MODELS.items()
        if config['provider'] == provider
    }


def get_model_info(model_id: str) -> Dict[str, Any]:
    """
    Get information about a specific model.

    Args:
        model_id: Model identifier

    Returns:
        Model configuration dictionary or None if not found
    """
    return AVAILABLE_MODELS.get(model_id)


def is_valid_model(model_id: str) -> bool:
    """
    Check if a model ID is valid.

    Args:
        model_id: Model identifier

    Returns:
        True if model exists, False otherwise
    """
    return model_id in AVAILABLE_MODELS


def get_model_for_ui() -> List[Dict[str, Any]]:
    """
    Get models formatted for UI display (grouped by provider).

    Returns:
        List of model groups with provider and models
    """
    providers = {}

    for model_id, config in AVAILABLE_MODELS.items():
        provider = config['provider']
        if provider not in providers:
            providers[provider] = []

        providers[provider].append({
            'id': model_id,
            'name': config['name'],
            'description': config['description'],
            'category': config['category'],
            'recommended_for': config['recommended_for']
        })

    # Convert to list format
    result = []
    for provider, models in providers.items():
        result.append({
            'provider': provider,
            'models': models
        })

    return result


def get_generation_models() -> List[Dict[str, str]]:
    """Get list of models suitable for generation (bias injection, debiasing).
    
    Excludes Vertex AI models (openapi, vertex_sdk endpoint types).
    Only includes Bedrock models.
    """
    models = []
    for model_id, config in AVAILABLE_MODELS.items():
        # Only include models that support generation AND are not Vertex AI models
        if 'generation' in config['recommended_for']:
            endpoint_type = config.get('endpoint_type', '')
            # Exclude Vertex AI models (openapi and vertex_sdk)
            if endpoint_type not in ['openapi', 'vertex_sdk']:
                models.append({
                    'id': model_id,
                    'name': config['name'],
                    'provider': config['provider'],
                    'description': config['description']
                })
    return models


def get_evaluation_models() -> List[Dict[str, str]]:
    """Get list of models suitable for evaluation.
    
    Excludes Vertex AI models (openapi, vertex_sdk endpoint types).
    Only includes Bedrock models.
    """
    models = []
    for model_id, config in AVAILABLE_MODELS.items():
        # Only include models that support evaluation AND are not Vertex AI models
        if 'evaluation' in config['recommended_for']:
            endpoint_type = config.get('endpoint_type', '')
            # Exclude Vertex AI models (openapi and vertex_sdk)
            if endpoint_type not in ['openapi', 'vertex_sdk']:
                models.append({
                    'id': model_id,
                    'name': config['name'],
                    'provider': config['provider'],
                    'description': config['description']
                })
    return models
