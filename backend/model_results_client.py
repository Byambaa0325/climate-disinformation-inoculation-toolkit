"""
Model Evaluation Results Client

Provides access to pre-generated model evaluation results.
These results contain Turn 1 and Turn 2 responses from various models
tested with the EMGSD dataset.
"""

import json
import os
from typing import List, Dict, Optional, Any
from pathlib import Path
import glob


class ModelResultsClient:
    """
    Client for accessing model evaluation results.

    The results contain responses from various LLMs (Bedrock and Ollama)
    evaluated on the EMGSD multi-turn bias injection dataset.

    Example:
        >>> client = ModelResultsClient()
        >>> models = client.get_available_models()
        >>> results = client.get_model_results('llama3.1:8b')
        >>> len(results)
        800
    """

    # Model categories
    BEDROCK_MODELS = [
        'us.anthropic.claude-3-5-sonnet-20241022-v2:0',
        'us.anthropic.claude-3-sonnet-20240229-v1:0',
        'us.anthropic.claude-3-5-haiku-20241022-v1:0',
        'us.anthropic.claude-3-haiku-20240307-v1:0',
        'us.meta.llama3-1-70b-instruct-v1:0',
        'us.amazon.nova-pro-v1:0',
        'us.amazon.nova-lite-v1:0',
        'us.amazon.nova-micro-v1:0',
    ]

    OLLAMA_MODELS = [
        # Ollama models excluded per user request
        # 'llama3.1:8b',
        # 'llama3.2:3b',
        # 'llama3.2:1b',
        # 'mistral:7b',
        # 'gemma2:9b',
        # 'qwen2.5:7b',
        # 'deepseek-llm:7b',  # Explicitly excluded
        # 'gpt-oss:20b-cloud',
    ]

    def __init__(self, results_dir: Optional[str] = None):
        """
        Initialize results client.

        Args:
            results_dir: Directory containing evaluation JSON files.
                        If None, uses default location.
        """
        if results_dir is None:
            current_dir = Path(__file__).parent
            results_dir = current_dir.parent / "data" / "model_evaluations"

        self.results_dir = Path(results_dir)
        if not self.results_dir.exists():
            raise FileNotFoundError(f"Results directory not found at {self.results_dir}")

        # Load all available results
        self._load_results()

    def _load_results(self):
        """Load all evaluation result files"""
        self.results = {}
        self.model_metadata = {}

        # Find all evaluation JSON files
        pattern = str(self.results_dir / "evaluation_*.json")
        result_files = glob.glob(pattern)

        for file_path in result_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Extract model ID from first entry
                if data and len(data) > 0:
                    model_id = data[0].get('model_id', 'unknown')
                    self.results[model_id] = data

                    # Store metadata
                    self.model_metadata[model_id] = {
                        'total_entries': len(data),
                        'file_path': file_path,
                        'is_bedrock': model_id in self.BEDROCK_MODELS,
                        'is_ollama': model_id in self.OLLAMA_MODELS,
                        'supports_live_generation': model_id in self.BEDROCK_MODELS,
                    }

            except Exception as e:
                print(f"Warning: Could not load {file_path}: {e}")

    def get_available_models(self) -> List[str]:
        """
        Get list of available model IDs.

        Returns:
            List of model IDs

        Example:
            >>> client = ModelResultsClient()
            >>> models = client.get_available_models()
            >>> 'llama3.1:8b' in models
            True
        """
        return list(self.results.keys())

    def get_bedrock_models(self) -> List[str]:
        """Get list of available Bedrock models"""
        return [
            model_id for model_id in self.results.keys()
            if self.model_metadata[model_id]['is_bedrock']
        ]

    def get_ollama_models(self) -> List[str]:
        """Get list of available Ollama models"""
        return [
            model_id for model_id in self.results.keys()
            if self.model_metadata[model_id]['is_ollama']
        ]

    def get_model_results(self, model_id: str) -> List[Dict[str, Any]]:
        """
        Get all results for a specific model.

        Args:
            model_id: Model identifier

        Returns:
            List of evaluation results

        Example:
            >>> client = ModelResultsClient()
            >>> results = client.get_model_results('llama3.1:8b')
            >>> len(results)
            800
        """
        if model_id not in self.results:
            available = ', '.join(self.get_available_models())
            raise ValueError(
                f"Model '{model_id}' not found. "
                f"Available models: {available}"
            )
        return self.results[model_id]

    def get_result_by_index(self, model_id: str, entry_index: int) -> Dict[str, Any]:
        """
        Get a specific result entry by index.

        Args:
            model_id: Model identifier
            entry_index: Entry index in the dataset

        Returns:
            Evaluation result entry

        Example:
            >>> client = ModelResultsClient()
            >>> entry = client.get_result_by_index('llama3.1:8b', 0)
            >>> entry['target_question']
            'The supervisor is'
        """
        results = self.get_model_results(model_id)

        # Find entry with matching index
        for entry in results:
            if entry.get('entry_index') == entry_index:
                return entry

        raise ValueError(
            f"No result found for model '{model_id}' with entry_index {entry_index}"
        )

    def get_results_by_bias_type(
        self,
        model_id: str,
        bias_type: str
    ) -> List[Dict[str, Any]]:
        """
        Get all results for a specific bias type.

        Args:
            model_id: Model identifier
            bias_type: Bias type (e.g., 'confirmation_bias')

        Returns:
            List of matching results

        Example:
            >>> client = ModelResultsClient()
            >>> results = client.get_results_by_bias_type(
            ...     'llama3.1:8b',
            ...     'confirmation_bias'
            ... )
        """
        results = self.get_model_results(model_id)
        return [r for r in results if r.get('bias_type') == bias_type]

    def get_results_by_stereotype_type(
        self,
        model_id: str,
        stereotype_type: str
    ) -> List[Dict[str, Any]]:
        """
        Get all results for a specific stereotype type.

        Args:
            model_id: Model identifier
            stereotype_type: Stereotype type (e.g., 'profession', 'gender')

        Returns:
            List of matching results
        """
        results = self.get_model_results(model_id)
        return [
            r for r in results
            if r.get('emgsd_stereotype_type') == stereotype_type
        ]

    def get_model_metadata(self, model_id: str) -> Dict[str, Any]:
        """
        Get metadata for a model.

        Args:
            model_id: Model identifier

        Returns:
            Dictionary with metadata

        Example:
            >>> client = ModelResultsClient()
            >>> meta = client.get_model_metadata('llama3.1:8b')
            >>> meta['supports_live_generation']
            False
        """
        if model_id not in self.model_metadata:
            raise ValueError(f"Model '{model_id}' not found")
        return self.model_metadata[model_id]

    def supports_live_generation(self, model_id: str) -> bool:
        """
        Check if model supports live generation (Bedrock models only).

        Args:
            model_id: Model identifier

        Returns:
            True if model supports live generation

        Example:
            >>> client = ModelResultsClient()
            >>> client.supports_live_generation('llama3.1:8b')
            False
            >>> client.supports_live_generation('us.amazon.nova-pro-v1:0')
            True
        """
        meta = self.get_model_metadata(model_id)
        return meta['supports_live_generation']

    def get_statistics(self, model_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics for a model or all models.

        Args:
            model_id: Model identifier (if None, returns stats for all models)

        Returns:
            Dictionary with statistics

        Example:
            >>> client = ModelResultsClient()
            >>> stats = client.get_statistics('llama3.1:8b')
            >>> stats['total_entries']
            800
        """
        if model_id is not None:
            # Stats for specific model
            results = self.get_model_results(model_id)

            bias_type_counts = {}
            stereotype_type_counts = {}

            for entry in results:
                bias_type = entry.get('bias_type', 'unknown')
                stereotype_type = entry.get('emgsd_stereotype_type', 'unknown')

                bias_type_counts[bias_type] = bias_type_counts.get(bias_type, 0) + 1
                stereotype_type_counts[stereotype_type] = stereotype_type_counts.get(stereotype_type, 0) + 1

            return {
                'model_id': model_id,
                'total_entries': len(results),
                'bias_type_counts': bias_type_counts,
                'stereotype_type_counts': stereotype_type_counts,
                'supports_live_generation': self.supports_live_generation(model_id),
            }
        else:
            # Stats for all models
            return {
                'total_models': len(self.results),
                'bedrock_models': len(self.get_bedrock_models()),
                'ollama_models': len(self.get_ollama_models()),
                'models_with_live_generation': len(self.get_bedrock_models()),
                'models_static_only': len(self.get_ollama_models()),
            }

    def compare_models(
        self,
        entry_index: int,
        bias_type: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compare responses from all models for a specific entry.

        Args:
            entry_index: Entry index in the dataset
            bias_type: Optional bias type filter

        Returns:
            Dictionary mapping model_id to result entry

        Example:
            >>> client = ModelResultsClient()
            >>> comparison = client.compare_models(0, 'confirmation_bias')
            >>> comparison['llama3.1:8b']['turn2_response']
        """
        comparison = {}

        for model_id in self.get_available_models():
            try:
                entry = self.get_result_by_index(model_id, entry_index)
                if bias_type is None or entry.get('bias_type') == bias_type:
                    comparison[model_id] = entry
            except ValueError:
                # Model doesn't have this entry
                continue

        return comparison


def print_results_info():
    """Print results information"""
    try:
        client = ModelResultsClient()

        print("=" * 80)
        print("MODEL EVALUATION RESULTS INFO")
        print("=" * 80)

        stats = client.get_statistics()
        print(f"\nTotal Models: {stats['total_models']}")
        print(f"  - Bedrock (Live Generation): {stats['bedrock_models']}")
        print(f"  - Ollama (Static Benchmark): {stats['ollama_models']}")

        print("\n" + "-" * 80)
        print("BEDROCK MODELS (Support Live Generation):")
        print("-" * 80)
        for model_id in client.get_bedrock_models():
            meta = client.get_model_metadata(model_id)
            print(f"  {model_id} ({meta['total_entries']} entries)")

        print("\n" + "-" * 80)
        print("OLLAMA MODELS (Static Benchmark Only):")
        print("-" * 80)
        for model_id in client.get_ollama_models():
            meta = client.get_model_metadata(model_id)
            print(f"  {model_id} ({meta['total_entries']} entries)")

        print("\n" + "=" * 80)
        print("SAMPLE ENTRY:")
        print("=" * 80)
        models = client.get_available_models()
        if models:
            sample_model = models[0]
            results = client.get_model_results(sample_model)
            if results:
                entry = results[0]
                print(f"Model: {sample_model}")
                print(f"Entry Index: {entry['entry_index']}")
                print(f"Bias Type: {entry['bias_type']}")
                print(f"Target Question: {entry['target_question']}")
                print(f"Turn 1 Question: {entry['turn1_question'][:80]}...")
                print(f"Turn 2 Response: {entry['turn2_response'][:80]}...")
                print(f"Control Response: {entry['control_response'][:80]}...")

        print("=" * 80)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print_results_info()
