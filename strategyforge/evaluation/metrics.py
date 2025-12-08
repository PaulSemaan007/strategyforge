"""
Evaluation metrics for LLM wargaming capabilities.

This module defines the core metrics used to evaluate how well
LLMs perform in military decision-making scenarios. These metrics
directly address the question: "How effective are LLMs at wargaming?"

Metrics Categories:
1. Geospatial Accuracy - Can the LLM reason about distances and terrain?
2. Strategic Coherence - Are decisions logically consistent?
3. Resource Awareness - Does the LLM track logistics properly?
4. Adversarial Reasoning - Does the LLM anticipate opponent moves?
5. Doctrinal Alignment - Do decisions match military best practices?
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
import re
import json


class MetricCategory(Enum):
    """Categories of evaluation metrics."""
    GEOSPATIAL = "geospatial"
    STRATEGIC = "strategic"
    RESOURCE = "resource"
    ADVERSARIAL = "adversarial"
    DOCTRINAL = "doctrinal"


@dataclass
class MetricResult:
    """Result of a single metric evaluation."""
    name: str
    category: MetricCategory
    score: float  # 0.0 to 1.0
    max_score: float = 1.0
    details: str = ""
    evidence: list[str] = field(default_factory=list)

    @property
    def percentage(self) -> float:
        """Get score as percentage."""
        return (self.score / self.max_score) * 100

    @property
    def grade(self) -> str:
        """Get letter grade."""
        pct = self.percentage
        if pct >= 90:
            return "A"
        elif pct >= 80:
            return "B"
        elif pct >= 70:
            return "C"
        elif pct >= 60:
            return "D"
        else:
            return "F"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "category": self.category.value,
            "score": self.score,
            "max_score": self.max_score,
            "percentage": self.percentage,
            "grade": self.grade,
            "details": self.details,
            "evidence": self.evidence
        }


@dataclass
class EvaluationReport:
    """Complete evaluation report for an LLM session."""
    model_name: str
    scenario_name: str
    total_turns: int
    metrics: list[MetricResult] = field(default_factory=list)
    raw_responses: list[dict] = field(default_factory=list)

    @property
    def overall_score(self) -> float:
        """Calculate weighted overall score."""
        if not self.metrics:
            return 0.0
        return sum(m.score for m in self.metrics) / len(self.metrics)

    @property
    def overall_percentage(self) -> float:
        """Get overall score as percentage."""
        return self.overall_score * 100

    @property
    def category_scores(self) -> dict[str, float]:
        """Get average scores by category."""
        categories = {}
        for metric in self.metrics:
            cat = metric.category.value
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(metric.score)

        return {cat: sum(scores) / len(scores) for cat, scores in categories.items()}

    def to_dict(self) -> dict:
        return {
            "model_name": self.model_name,
            "scenario_name": self.scenario_name,
            "total_turns": self.total_turns,
            "overall_score": self.overall_score,
            "overall_percentage": self.overall_percentage,
            "category_scores": self.category_scores,
            "metrics": [m.to_dict() for m in self.metrics]
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def summary(self) -> str:
        """Generate human-readable summary."""
        lines = [
            f"=== Evaluation Report ===",
            f"Model: {self.model_name}",
            f"Scenario: {self.scenario_name}",
            f"Turns: {self.total_turns}",
            f"",
            f"Overall Score: {self.overall_percentage:.1f}%",
            f"",
            "Category Breakdown:"
        ]

        for cat, score in self.category_scores.items():
            lines.append(f"  {cat.capitalize()}: {score * 100:.1f}%")

        lines.append("")
        lines.append("Individual Metrics:")

        for metric in self.metrics:
            lines.append(f"  [{metric.grade}] {metric.name}: {metric.percentage:.1f}%")
            if metric.details:
                lines.append(f"      {metric.details}")

        return "\n".join(lines)


class GeospatialMetrics:
    """
    Metrics for evaluating geospatial reasoning accuracy.

    Tests whether the LLM can:
    - Correctly estimate distances between positions
    - Understand terrain characteristics
    - Reason about operational ranges
    """

    @staticmethod
    def evaluate_distance_claims(
        response: str,
        ground_truth: dict[str, float]
    ) -> MetricResult:
        """
        Evaluate accuracy of distance claims in a response.

        Args:
            response: The LLM's response text
            ground_truth: Dict mapping position pairs to actual distances

        Returns:
            MetricResult with distance accuracy score
        """
        # Extract distance claims from response
        # Pattern: "X km", "X kilometers", "approximately X km"
        distance_pattern = r'(\d+(?:\.\d+)?)\s*(?:km|kilometers?|klicks)'
        claimed_distances = re.findall(distance_pattern, response, re.IGNORECASE)

        if not claimed_distances:
            return MetricResult(
                name="Distance Accuracy",
                category=MetricCategory.GEOSPATIAL,
                score=0.5,  # Neutral if no claims made
                details="No distance claims found in response",
                evidence=[]
            )

        # For now, check if claimed distances are in reasonable range
        # In production, this would match specific claims to ground truth
        errors = []
        reasonable_count = 0

        for dist_str in claimed_distances:
            dist = float(dist_str)
            # Taiwan Strait context: distances should be 0-500km typically
            if 0 < dist < 1000:
                reasonable_count += 1
            else:
                errors.append(f"Unreasonable distance: {dist}km")

        score = reasonable_count / len(claimed_distances) if claimed_distances else 0.5

        return MetricResult(
            name="Distance Accuracy",
            category=MetricCategory.GEOSPATIAL,
            score=score,
            details=f"Found {len(claimed_distances)} distance claims, {reasonable_count} reasonable",
            evidence=errors[:5]  # Limit evidence
        )

    @staticmethod
    def evaluate_grid_reference_usage(response: str) -> MetricResult:
        """
        Evaluate whether the LLM uses proper grid references.

        Military planning requires precise location references.
        """
        # Pattern for grid references like "TW-1001" or "Grid TW-1001"
        grid_pattern = r'(?:Grid\s+)?([A-Z]{2}-\d{4})'
        grids = re.findall(grid_pattern, response)

        if not grids:
            return MetricResult(
                name="Grid Reference Usage",
                category=MetricCategory.GEOSPATIAL,
                score=0.3,
                details="No grid references used - imprecise positioning",
                evidence=[]
            )

        # Check for valid grid format
        valid_grids = [g for g in grids if len(g) == 7]  # XX-XXXX format

        score = min(1.0, len(valid_grids) / 3)  # Expect at least 3 references

        return MetricResult(
            name="Grid Reference Usage",
            category=MetricCategory.GEOSPATIAL,
            score=score,
            details=f"Used {len(valid_grids)} valid grid references",
            evidence=valid_grids[:5]
        )

    @staticmethod
    def evaluate_terrain_awareness(response: str) -> MetricResult:
        """
        Evaluate whether the LLM considers terrain in its reasoning.
        """
        terrain_keywords = [
            "terrain", "elevation", "mountain", "coastal", "strait",
            "water", "land", "beach", "port", "urban", "defensive",
            "chokepoint", "high ground", "cover", "concealment"
        ]

        found_keywords = []
        response_lower = response.lower()

        for keyword in terrain_keywords:
            if keyword in response_lower:
                found_keywords.append(keyword)

        score = min(1.0, len(found_keywords) / 5)  # Expect 5+ terrain considerations

        return MetricResult(
            name="Terrain Awareness",
            category=MetricCategory.GEOSPATIAL,
            score=score,
            details=f"Referenced {len(found_keywords)} terrain concepts",
            evidence=found_keywords
        )


class StrategicMetrics:
    """
    Metrics for evaluating strategic reasoning quality.

    Tests whether the LLM can:
    - Make logically consistent decisions
    - Connect actions to objectives
    - Consider risks and mitigations
    """

    @staticmethod
    def evaluate_objective_alignment(
        response: str,
        objectives: list[str]
    ) -> MetricResult:
        """
        Evaluate whether the response aligns with stated objectives.
        """
        response_lower = response.lower()
        aligned_objectives = []

        for obj in objectives:
            # Check if objective keywords appear in response
            obj_words = obj.lower().split()
            if any(word in response_lower for word in obj_words if len(word) > 3):
                aligned_objectives.append(obj)

        score = len(aligned_objectives) / len(objectives) if objectives else 0.5

        return MetricResult(
            name="Objective Alignment",
            category=MetricCategory.STRATEGIC,
            score=score,
            details=f"Addressed {len(aligned_objectives)}/{len(objectives)} objectives",
            evidence=aligned_objectives
        )

    @staticmethod
    def evaluate_reasoning_structure(response: str) -> MetricResult:
        """
        Evaluate whether the response follows structured reasoning.

        Good military planning includes:
        - Situation assessment
        - Recommended action
        - Rationale
        - Risks and mitigations
        """
        structure_elements = {
            "situation": ["situation", "assessment", "current state", "intelligence"],
            "action": ["recommend", "action", "execute", "deploy", "move"],
            "rationale": ["because", "rationale", "reason", "therefore", "in order to"],
            "risk": ["risk", "mitigat", "contingenc", "fallback", "if"]
        }

        found_elements = []
        response_lower = response.lower()

        for element, keywords in structure_elements.items():
            if any(kw in response_lower for kw in keywords):
                found_elements.append(element)

        score = len(found_elements) / len(structure_elements)

        return MetricResult(
            name="Reasoning Structure",
            category=MetricCategory.STRATEGIC,
            score=score,
            details=f"Included {len(found_elements)}/4 reasoning elements",
            evidence=found_elements
        )

    @staticmethod
    def evaluate_consistency(
        current_response: str,
        previous_responses: list[str]
    ) -> MetricResult:
        """
        Evaluate consistency with previous decisions.
        """
        if not previous_responses:
            return MetricResult(
                name="Decision Consistency",
                category=MetricCategory.STRATEGIC,
                score=0.8,  # Assume good for first response
                details="First response - no history to compare",
                evidence=[]
            )

        # Check for contradictions (simplified)
        contradiction_phrases = [
            "instead", "cancel", "abort", "reverse", "opposite"
        ]

        contradictions = []
        response_lower = current_response.lower()

        for phrase in contradiction_phrases:
            if phrase in response_lower:
                contradictions.append(phrase)

        # Some contradictions are okay (adapting to situation)
        score = max(0.5, 1.0 - (len(contradictions) * 0.2))

        return MetricResult(
            name="Decision Consistency",
            category=MetricCategory.STRATEGIC,
            score=score,
            details=f"Found {len(contradictions)} potential direction changes",
            evidence=contradictions
        )


class AdversarialMetrics:
    """
    Metrics for evaluating adversarial reasoning.

    Tests whether the LLM can:
    - Anticipate opponent actions
    - Consider counter-moves
    - Think multiple steps ahead
    """

    @staticmethod
    def evaluate_opponent_modeling(response: str) -> MetricResult:
        """
        Evaluate whether the response considers opponent actions.
        """
        opponent_keywords = [
            "enemy", "opponent", "adversary", "red force", "blue force",
            "they will", "they may", "expect them", "anticipate",
            "counter", "response", "react", "their move"
        ]

        found = []
        response_lower = response.lower()

        for keyword in opponent_keywords:
            if keyword in response_lower:
                found.append(keyword)

        score = min(1.0, len(found) / 4)

        return MetricResult(
            name="Opponent Modeling",
            category=MetricCategory.ADVERSARIAL,
            score=score,
            details=f"Referenced opponent {len(found)} times",
            evidence=found[:5]
        )

    @staticmethod
    def evaluate_multi_step_thinking(response: str) -> MetricResult:
        """
        Evaluate whether the response shows multi-step planning.
        """
        multi_step_indicators = [
            "then", "after that", "next", "subsequently", "phase",
            "step 1", "step 2", "first", "second", "finally",
            "if they", "in response"
        ]

        found = []
        response_lower = response.lower()

        for indicator in multi_step_indicators:
            if indicator in response_lower:
                found.append(indicator)

        score = min(1.0, len(found) / 3)

        return MetricResult(
            name="Multi-Step Planning",
            category=MetricCategory.ADVERSARIAL,
            score=score,
            details=f"Found {len(found)} multi-step indicators",
            evidence=found[:5]
        )


def evaluate_response(
    response: str,
    scenario_objectives: list[str] = None,
    previous_responses: list[str] = None,
    ground_truth_distances: dict = None
) -> list[MetricResult]:
    """
    Run all evaluation metrics on a response.

    Args:
        response: The LLM response to evaluate
        scenario_objectives: List of scenario objectives
        previous_responses: Previous responses for consistency check
        ground_truth_distances: Known distances for accuracy check

    Returns:
        List of MetricResult objects
    """
    results = []

    # Geospatial metrics
    results.append(GeospatialMetrics.evaluate_distance_claims(
        response, ground_truth_distances or {}
    ))
    results.append(GeospatialMetrics.evaluate_grid_reference_usage(response))
    results.append(GeospatialMetrics.evaluate_terrain_awareness(response))

    # Strategic metrics
    results.append(StrategicMetrics.evaluate_objective_alignment(
        response, scenario_objectives or []
    ))
    results.append(StrategicMetrics.evaluate_reasoning_structure(response))
    results.append(StrategicMetrics.evaluate_consistency(
        response, previous_responses or []
    ))

    # Adversarial metrics
    results.append(AdversarialMetrics.evaluate_opponent_modeling(response))
    results.append(AdversarialMetrics.evaluate_multi_step_thinking(response))

    return results
