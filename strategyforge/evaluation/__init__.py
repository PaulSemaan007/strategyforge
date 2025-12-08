"""
LLM Evaluation Framework for Wargaming.

This module provides comprehensive evaluation tooling to measure
the effectiveness of LLMs applied to military decision-making:
- Geospatial accuracy metrics
- Strategic coherence analysis
- Resource awareness tracking
- Adversarial reasoning assessment
"""

from .metrics import EvaluationReport, MetricResult, evaluate_response
from .runner import EvaluationRunner
from .benchmarks import get_benchmark, list_benchmarks

__all__ = [
    "EvaluationReport",
    "MetricResult", 
    "EvaluationRunner",
    "evaluate_response",
    "get_benchmark",
    "list_benchmarks"
]
