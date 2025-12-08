"""
LLM Evaluation Framework for Wargaming.

This module provides comprehensive evaluation tooling to measure
the effectiveness of LLMs applied to military decision-making:
- Geospatial accuracy metrics
- Strategic coherence analysis
- Resource awareness tracking
- Adversarial reasoning assessment
"""

from .metrics import EvaluationMetrics
from .runner import EvaluationRunner

__all__ = ["EvaluationMetrics", "EvaluationRunner"]
