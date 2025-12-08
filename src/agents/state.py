"""
State management for the wargaming simulation.

Defines the shared state that flows through the LangGraph agent graph,
tracking game state, agent messages, and evaluation metrics.
"""

from dataclasses import dataclass, field
from typing import Annotated, Literal, TypedDict
from langgraph.graph.message import add_messages


class Position(TypedDict):
    """Geographic position with latitude and longitude."""
    lat: float
    lon: float
    grid_ref: str  # Military grid reference


class Unit(TypedDict):
    """A military unit in the simulation."""
    id: str
    name: str
    type: Literal["air", "naval", "ground", "cyber"]
    force: Literal["blue", "red"]
    position: Position
    status: Literal["ready", "engaged", "damaged", "destroyed"]
    capabilities: list[str]


class AgentAction(TypedDict):
    """An action taken by an agent."""
    agent: Literal["blue_commander", "red_commander", "analyst"]
    turn: int
    action_type: str
    description: str
    grid_references: list[str]
    units_involved: list[str]
    reasoning: str


class EvaluationScore(TypedDict):
    """Evaluation scores for an agent's action."""
    geospatial_accuracy: float  # 1-10
    strategic_coherence: float  # 1-10
    resource_efficiency: float  # 1-10
    adversarial_awareness: float  # 1-10
    risk_calibration: float  # 1-10
    overall: float  # Weighted average


class GameState(TypedDict):
    """
    The complete state of a wargaming simulation.

    This state flows through the LangGraph and is updated by each agent.
    Uses Annotated types for LangGraph's automatic state management.
    """
    # Simulation metadata
    scenario_name: str
    turn_number: int
    phase: Literal["blue_planning", "red_planning", "analysis", "resolution"]

    # Message history (LangGraph managed)
    messages: Annotated[list, add_messages]

    # Force dispositions
    blue_units: list[Unit]
    red_units: list[Unit]

    # Action history
    action_history: list[AgentAction]

    # Evaluation tracking
    blue_scores: list[EvaluationScore]
    red_scores: list[EvaluationScore]

    # Scenario-specific data
    objectives: dict
    terrain_data: dict

    # Simulation control
    is_complete: bool
    winner: Literal["blue", "red", "contested", None]


def create_initial_state(
    scenario_name: str,
    blue_units: list[Unit],
    red_units: list[Unit],
    objectives: dict,
    terrain_data: dict = None
) -> GameState:
    """Create the initial game state for a new simulation."""
    return GameState(
        scenario_name=scenario_name,
        turn_number=1,
        phase="blue_planning",
        messages=[],
        blue_units=blue_units,
        red_units=red_units,
        action_history=[],
        blue_scores=[],
        red_scores=[],
        objectives=objectives,
        terrain_data=terrain_data or {},
        is_complete=False,
        winner=None
    )


def format_game_state_for_agent(state: GameState, for_agent: str) -> str:
    """
    Format the game state as a string for agent consumption.

    Filters information based on fog of war - agents only see
    what their force would realistically know.
    """
    lines = [
        f"# Scenario: {state['scenario_name']}",
        f"## Turn {state['turn_number']} - Phase: {state['phase']}",
        "",
        "## Objectives",
    ]

    for obj_name, obj_data in state['objectives'].items():
        lines.append(f"- {obj_name}: {obj_data.get('description', 'N/A')}")

    lines.append("")
    lines.append("## Force Disposition")

    # Show own forces in detail
    if for_agent in ["blue_commander", "analyst"]:
        lines.append("### Blue Forces (Friendly)")
        for unit in state['blue_units']:
            lines.append(
                f"- {unit['name']} ({unit['type']}): "
                f"Grid {unit['position']['grid_ref']} - {unit['status']}"
            )

    if for_agent in ["red_commander", "analyst"]:
        lines.append("### Red Forces")
        for unit in state['red_units']:
            lines.append(
                f"- {unit['name']} ({unit['type']}): "
                f"Grid {unit['position']['grid_ref']} - {unit['status']}"
            )

    # Show limited intel about opposing force (fog of war)
    if for_agent == "blue_commander":
        lines.append("")
        lines.append("### Red Forces (Intelligence Estimate)")
        lines.append("- Known positions based on last reconnaissance")
        # In a full implementation, this would show partial/outdated info

    if for_agent == "red_commander":
        lines.append("")
        lines.append("### Blue Forces (Intelligence Estimate)")
        lines.append("- Known positions based on surveillance")

    # Recent actions
    if state['action_history']:
        lines.append("")
        lines.append("## Recent Actions")
        for action in state['action_history'][-5:]:  # Last 5 actions
            lines.append(f"- Turn {action['turn']} [{action['agent']}]: {action['description']}")

    return "\n".join(lines)
