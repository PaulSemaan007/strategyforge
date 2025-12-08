"""
Evaluation runner for LLM wargaming benchmarks.

This module runs benchmark tests against LLMs and generates
comprehensive evaluation reports.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

from .benchmarks import BenchmarkSuite, BenchmarkCase, get_benchmark
from .metrics import (
    MetricResult,
    EvaluationReport,
    evaluate_response,
    MetricCategory
)


@dataclass
class BenchmarkResult:
    """Result of running a single benchmark case."""
    case_id: str
    case_name: str
    prompt: str
    response: str
    metrics: list[MetricResult]
    expected_found: list[str]
    expected_missing: list[str]
    execution_time_ms: float

    @property
    def score(self) -> float:
        """Average score across all metrics."""
        if not self.metrics:
            return 0.0
        return sum(m.score for m in self.metrics) / len(self.metrics)

    @property
    def expected_coverage(self) -> float:
        """Percentage of expected elements found."""
        total = len(self.expected_found) + len(self.expected_missing)
        if total == 0:
            return 1.0
        return len(self.expected_found) / total

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "case_name": self.case_name,
            "score": self.score,
            "expected_coverage": self.expected_coverage,
            "execution_time_ms": self.execution_time_ms,
            "expected_found": self.expected_found,
            "expected_missing": self.expected_missing,
            "metrics": [m.to_dict() for m in self.metrics],
            "prompt": self.prompt[:500] + "..." if len(self.prompt) > 500 else self.prompt,
            "response": self.response[:1000] + "..." if len(self.response) > 1000 else self.response
        }


class EvaluationRunner:
    """
    Runs evaluation benchmarks against LLMs.

    Usage:
        runner = EvaluationRunner(model_name="llama3.1:8b")
        report = runner.run_benchmark("quick")
        print(report.summary())
    """

    SYSTEM_PROMPT = """You are a military strategic analyst participating in a wargaming exercise.
Provide detailed, professional responses that demonstrate:
- Precise geographic and distance calculations
- Structured military reasoning
- Consideration of adversary actions
- Risk assessment and mitigation

Use grid references when discussing positions.
Show your calculations when making quantitative claims.
Structure your response clearly with sections."""

    def __init__(
        self,
        model_name: str = "llama3.1:8b",
        temperature: float = 0.3,  # Lower temp for more consistent evaluation
        verbose: bool = False
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.verbose = verbose
        self.llm = ChatOllama(
            model=model_name,
            temperature=temperature
        )

    def run_benchmark(
        self,
        benchmark_name: str,
        max_cases: Optional[int] = None
    ) -> EvaluationReport:
        """
        Run a complete benchmark suite.

        Args:
            benchmark_name: Name of benchmark to run
            max_cases: Limit number of cases (for testing)

        Returns:
            EvaluationReport with all results
        """
        suite = get_benchmark(benchmark_name)
        cases = suite.cases[:max_cases] if max_cases else suite.cases

        if self.verbose:
            print(f"Running benchmark: {suite.name}")
            print(f"Cases: {len(cases)}")
            print("-" * 50)

        results = []
        all_metrics = []

        for i, case in enumerate(cases):
            if self.verbose:
                print(f"[{i+1}/{len(cases)}] {case.name}...")

            result = self._run_case(case)
            results.append(result)
            all_metrics.extend(result.metrics)

            if self.verbose:
                print(f"  Score: {result.score:.2f}")
                print(f"  Expected coverage: {result.expected_coverage:.1%}")

        # Create report
        report = EvaluationReport(
            model_name=self.model_name,
            scenario_name=benchmark_name,
            total_turns=len(cases),
            metrics=all_metrics,
            raw_responses=[r.to_dict() for r in results]
        )

        if self.verbose:
            print("-" * 50)
            print(f"Overall Score: {report.overall_percentage:.1f}%")

        return report

    def _run_case(self, case: BenchmarkCase) -> BenchmarkResult:
        """Run a single benchmark case."""
        import time
        start_time = time.time()

        # Build messages
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=case.prompt)
        ]

        # Get response
        response = self.llm.invoke(messages)
        response_text = response.content

        execution_time = (time.time() - start_time) * 1000

        # Check expected elements
        response_lower = response_text.lower()
        expected_found = []
        expected_missing = []

        for element in case.expected_elements:
            if element.lower() in response_lower:
                expected_found.append(element)
            else:
                expected_missing.append(element)

        # Run metrics evaluation
        metrics = evaluate_response(
            response_text,
            scenario_objectives=[],
            previous_responses=[],
            ground_truth_distances=case.ground_truth
        )

        return BenchmarkResult(
            case_id=case.id,
            case_name=case.name,
            prompt=case.prompt,
            response=response_text,
            metrics=metrics,
            expected_found=expected_found,
            expected_missing=expected_missing,
            execution_time_ms=execution_time
        )

    def run_single_prompt(self, prompt: str) -> tuple[str, list[MetricResult]]:
        """
        Run evaluation on a single custom prompt.

        Args:
            prompt: The prompt to evaluate

        Returns:
            Tuple of (response, metrics)
        """
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ]

        response = self.llm.invoke(messages)
        metrics = evaluate_response(response.content)

        return response.content, metrics


def save_report(report: EvaluationReport, output_path: Path) -> Path:
    """Save evaluation report to JSON file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(report.to_dict(), f, indent=2)

    return output_path


def load_report(input_path: Path) -> dict:
    """Load evaluation report from JSON file."""
    with open(input_path, "r") as f:
        return json.load(f)


def compare_reports(report1: dict, report2: dict) -> dict:
    """Compare two evaluation reports."""
    return {
        "model_1": report1["model_name"],
        "model_2": report2["model_name"],
        "score_1": report1["overall_percentage"],
        "score_2": report2["overall_percentage"],
        "difference": report1["overall_percentage"] - report2["overall_percentage"],
        "category_comparison": {
            cat: {
                "model_1": report1["category_scores"].get(cat, 0),
                "model_2": report2["category_scores"].get(cat, 0)
            }
            for cat in set(report1["category_scores"]) | set(report2["category_scores"])
        }
    }
