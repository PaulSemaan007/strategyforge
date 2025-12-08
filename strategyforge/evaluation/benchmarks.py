"""
Benchmark test suites for LLM wargaming evaluation.

This module provides structured test cases to measure LLM
performance on specific wargaming capabilities.

Benchmark Categories:
1. Geospatial Benchmarks - Distance calculations, terrain reasoning
2. Strategic Benchmarks - Decision quality, objective alignment
3. Adversarial Benchmarks - Opponent modeling, counter-planning
"""

from dataclasses import dataclass, field
from typing import Callable, Optional
import json
from pathlib import Path

from .metrics import MetricResult, MetricCategory, EvaluationReport


@dataclass
class BenchmarkCase:
    """A single test case in a benchmark."""
    id: str
    name: str
    prompt: str
    expected_elements: list[str]  # Keywords/concepts expected in response
    ground_truth: dict = field(default_factory=dict)  # For verifiable facts
    category: MetricCategory = MetricCategory.GEOSPATIAL
    difficulty: str = "medium"  # easy, medium, hard

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "prompt": self.prompt,
            "expected_elements": self.expected_elements,
            "ground_truth": self.ground_truth,
            "category": self.category.value,
            "difficulty": self.difficulty
        }


@dataclass
class BenchmarkSuite:
    """A collection of related benchmark cases."""
    name: str
    description: str
    cases: list[BenchmarkCase] = field(default_factory=list)

    def add_case(self, case: BenchmarkCase) -> None:
        self.cases.append(case)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "cases": [c.to_dict() for c in self.cases]
        }


# ============================================================================
# GEOSPATIAL BENCHMARKS
# ============================================================================

GEOSPATIAL_BENCHMARK = BenchmarkSuite(
    name="Geospatial Reasoning",
    description="Tests LLM ability to reason about distances, terrain, and geography"
)

# Distance estimation tests
GEOSPATIAL_BENCHMARK.add_case(BenchmarkCase(
    id="geo_001",
    name="Taiwan Strait Width",
    prompt="""You are a military analyst. A commander asks:
    "What is the approximate width of the Taiwan Strait at its narrowest point,
    and how long would it take a naval vessel traveling at 30 knots to cross it?"

    Provide a precise answer with calculations.""",
    expected_elements=["130", "180", "km", "hour", "knot", "nautical"],
    ground_truth={
        "strait_width_km": 130,
        "crossing_time_hours": 2.3  # 130km / (30 knots * 1.852 km/knot)
    },
    category=MetricCategory.GEOSPATIAL,
    difficulty="easy"
))

GEOSPATIAL_BENCHMARK.add_case(BenchmarkCase(
    id="geo_002",
    name="Fighter Intercept Range",
    prompt="""A Blue Force F-16 is stationed at Grid TW-1001 (Taipei area, 25.0N, 121.5E).
    Intelligence reports a Red bomber at Grid ML-0501 (26.0N, 119.5E).

    Calculate the distance between these positions and determine if the F-16,
    with an operational range of 800km, can intercept the bomber and return to base.

    Show your work.""",
    expected_elements=["distance", "km", "range", "intercept", "return", "fuel"],
    ground_truth={
        "distance_km": 220,  # Approximate
        "within_range": True,
        "round_trip_km": 440
    },
    category=MetricCategory.GEOSPATIAL,
    difficulty="medium"
))

GEOSPATIAL_BENCHMARK.add_case(BenchmarkCase(
    id="geo_003",
    name="Terrain Advantage Assessment",
    prompt="""Compare the defensive advantages of these two positions:

    Position A: Grid TW-1200 - Central Taiwan mountains, elevation 2000m
    Position B: Grid TS-3001 - Open water in Taiwan Strait

    Which position offers better defensive value for a ground force? Explain why.""",
    expected_elements=["mountain", "elevation", "cover", "defensi", "terrain", "water", "vulnerab"],
    ground_truth={
        "better_position": "A",
        "reason": "elevation and cover"
    },
    category=MetricCategory.GEOSPATIAL,
    difficulty="easy"
))

GEOSPATIAL_BENCHMARK.add_case(BenchmarkCase(
    id="geo_004",
    name="Multi-Asset Coordination",
    prompt="""Plan a coordinated strike requiring these assets to arrive simultaneously:

    - Fighter squadron at Grid TW-1001 (speed: 800 km/h)
    - Destroyer at Grid TS-4001 (speed: 50 km/h)
    - Submarine at Grid TS-5001 (speed: 40 km/h)

    Target: Grid TS-2500 (middle of strait)

    Calculate transit times and determine launch sequence for simultaneous arrival.""",
    expected_elements=["hour", "minute", "distance", "launch", "first", "arrive", "coordinat"],
    ground_truth={
        "requires_staggered_launch": True,
        "slowest_asset": "submarine"
    },
    category=MetricCategory.GEOSPATIAL,
    difficulty="hard"
))


# ============================================================================
# STRATEGIC BENCHMARKS
# ============================================================================

STRATEGIC_BENCHMARK = BenchmarkSuite(
    name="Strategic Reasoning",
    description="Tests LLM ability to make coherent strategic decisions"
)

STRATEGIC_BENCHMARK.add_case(BenchmarkCase(
    id="str_001",
    name="Objective Prioritization",
    prompt="""You command Blue Force with limited resources. Current objectives:

    1. Maintain air superiority over the strait (Value: 9/10)
    2. Protect port facilities (Value: 8/10)
    3. Interdict Red supply lines (Value: 7/10)
    4. Conduct reconnaissance (Value: 5/10)

    You can only fully resource TWO objectives. Which do you choose and why?

    Structure your response with clear reasoning.""",
    expected_elements=["priorit", "resource", "value", "air", "trade", "risk"],
    ground_truth={
        "should_consider_value": True,
        "should_explain_tradeoffs": True
    },
    category=MetricCategory.STRATEGIC,
    difficulty="medium"
))

STRATEGIC_BENCHMARK.add_case(BenchmarkCase(
    id="str_002",
    name="Risk Assessment",
    prompt="""Proposed Operation: Deploy carrier strike group 150km into contested waters
    to establish closer air support for amphibious operations.

    Threats:
    - Enemy anti-ship missiles (range: 200km)
    - Enemy submarine presence (2-3 confirmed)
    - Enemy air force (estimated 50 fighters)

    Assess the risks and recommend whether to proceed, modify, or cancel the operation.""",
    expected_elements=["risk", "missile", "range", "submarine", "recommend", "mitigat", "alternative"],
    ground_truth={
        "within_threat_range": True,
        "should_assess_all_threats": True
    },
    category=MetricCategory.STRATEGIC,
    difficulty="medium"
))

STRATEGIC_BENCHMARK.add_case(BenchmarkCase(
    id="str_003",
    name="Resource Allocation",
    prompt="""Your air wing has:
    - 40 fighters (currently: 30 available, 10 in maintenance)
    - 500 air-to-air missiles
    - Fuel for 200 sorties

    Mission requirements for next 48 hours:
    - Combat air patrol: 6 fighters continuous
    - Strike escort: 12 fighters for 4-hour mission
    - Quick reaction alert: 4 fighters on standby

    Create an allocation plan that meets requirements while maintaining reserves.""",
    expected_elements=["sortie", "rotation", "reserve", "maintenance", "available", "fuel", "missile"],
    ground_truth={
        "should_track_resources": True,
        "should_maintain_reserve": True
    },
    category=MetricCategory.STRATEGIC,
    difficulty="hard"
))


# ============================================================================
# ADVERSARIAL BENCHMARKS
# ============================================================================

ADVERSARIAL_BENCHMARK = BenchmarkSuite(
    name="Adversarial Reasoning",
    description="Tests LLM ability to model opponent behavior and plan counter-moves"
)

ADVERSARIAL_BENCHMARK.add_case(BenchmarkCase(
    id="adv_001",
    name="Opponent Prediction",
    prompt="""Red Force has been observed:
    - Massing naval assets at Grid ML-0501
    - Increasing air patrols over the strait
    - Moving amphibious ships from reserve to forward positions
    - Conducting electronic warfare exercises

    Based on these indicators, what are the three most likely Red Force actions
    in the next 72 hours? Rank by probability.""",
    expected_elements=["likely", "amphibious", "assault", "blockade", "strike", "probab", "indicator"],
    ground_truth={
        "should_analyze_indicators": True,
        "should_rank_options": True
    },
    category=MetricCategory.ADVERSARIAL,
    difficulty="medium"
))

ADVERSARIAL_BENCHMARK.add_case(BenchmarkCase(
    id="adv_002",
    name="Counter-Move Planning",
    prompt="""Intelligence confirms Red Force will launch an air strike against
    Blue Force airbases in 6 hours. Red Force assets:
    - 30 strike aircraft with escort
    - Electronic warfare support
    - Expected approach from the northwest

    You command Blue Force air defense. Plan your response, including:
    1. Defensive posture
    2. Counter-attack options
    3. Deception measures""",
    expected_elements=["intercept", "CAP", "SAM", "dispersal", "decoy", "counter", "radar"],
    ground_truth={
        "should_have_defensive_plan": True,
        "should_consider_counter": True
    },
    category=MetricCategory.ADVERSARIAL,
    difficulty="hard"
))

ADVERSARIAL_BENCHMARK.add_case(BenchmarkCase(
    id="adv_003",
    name="Deception Recognition",
    prompt="""Blue Force intelligence reports unusual Red Force activity:

    - Heavy radio traffic from Grid ML-1001 (normally quiet sector)
    - Visible movement of supply trucks toward forward positions
    - HOWEVER: No increase in fuel consumption at forward bases
    - HOWEVER: Key command units remain at rear positions

    Assess whether this activity represents a genuine offensive preparation
    or a deception operation. Explain your reasoning.""",
    expected_elements=["deception", "feint", "indicator", "genuine", "fuel", "command", "assess"],
    ground_truth={
        "likely_deception": True,
        "key_indicator": "fuel consumption"
    },
    category=MetricCategory.ADVERSARIAL,
    difficulty="hard"
))


# ============================================================================
# BENCHMARK REGISTRY
# ============================================================================

BENCHMARK_REGISTRY = {
    "geospatial": GEOSPATIAL_BENCHMARK,
    "strategic": STRATEGIC_BENCHMARK,
    "adversarial": ADVERSARIAL_BENCHMARK,
    "quick": BenchmarkSuite(
        name="Quick Evaluation",
        description="Fast benchmark with one case per category",
        cases=[
            GEOSPATIAL_BENCHMARK.cases[0],
            STRATEGIC_BENCHMARK.cases[0],
            ADVERSARIAL_BENCHMARK.cases[0]
        ]
    ),
    "full": BenchmarkSuite(
        name="Full Evaluation",
        description="Complete benchmark suite",
        cases=(
            GEOSPATIAL_BENCHMARK.cases +
            STRATEGIC_BENCHMARK.cases +
            ADVERSARIAL_BENCHMARK.cases
        )
    )
}


def get_benchmark(name: str) -> BenchmarkSuite:
    """Get a benchmark suite by name."""
    if name not in BENCHMARK_REGISTRY:
        raise ValueError(f"Unknown benchmark: {name}. Available: {list(BENCHMARK_REGISTRY.keys())}")
    return BENCHMARK_REGISTRY[name]


def list_benchmarks() -> list[dict]:
    """List all available benchmarks."""
    return [
        {
            "name": name,
            "description": suite.description,
            "num_cases": len(suite.cases)
        }
        for name, suite in BENCHMARK_REGISTRY.items()
    ]
