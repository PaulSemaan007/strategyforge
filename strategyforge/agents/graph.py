"""
LangGraph-based multi-agent wargaming simulation.

This module defines the agent graph that orchestrates the turn-based
wargaming simulation between Blue Force, Red Force, and Analyst agents.

Architecture:
    ┌─────────────────┐
    │  Start/Resume   │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ Blue Commander  │◄────────────────┐
    └────────┬────────┘                 │
             │                          │
             ▼                          │
    ┌─────────────────┐                 │
    │ Red Commander   │                 │
    └────────┬────────┘                 │
             │                          │
             ▼                          │
    ┌─────────────────┐                 │
    │    Analyst      │                 │
    └────────┬────────┘                 │
             │                          │
             ▼                          │
    ┌─────────────────┐    Continue     │
    │  Check End      │─────────────────┘
    └────────┬────────┘
             │ End
             ▼
    ┌─────────────────┐
    │   Final Report  │
    └─────────────────┘
"""

import os
from typing import Literal
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END

from .state import GameState, format_game_state_for_agent, AgentAction
from .prompts import AgentPrompts, format_turn_prompt


def create_llm(model_name: str = "llama-3.1-8b-instant", temperature: float = 0.7):
    """
    Create an LLM instance.

    Uses Groq (free cloud API) if GROQ_API_KEY is set, otherwise falls back to Ollama (local).
    """
    groq_api_key = os.environ.get("GROQ_API_KEY")

    if groq_api_key:
        # Use Groq (free cloud API)
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=model_name,
            temperature=temperature,
            api_key=groq_api_key,
        )
    else:
        # Fall back to local Ollama
        from langchain_ollama import ChatOllama
        # Map Groq model names to Ollama equivalents
        ollama_model = "llama3.1:8b" if "llama" in model_name.lower() else model_name
        return ChatOllama(
            model=ollama_model,
            temperature=temperature,
        )


def blue_commander_node(state: GameState) -> dict:
    """
    Blue Force Commander agent node.

    Analyzes the situation and recommends actions for friendly forces.
    """
    llm = create_llm()

    # Build the prompt
    system_prompt = AgentPrompts.get_blue_commander_prompt()
    game_context = format_game_state_for_agent(state, "blue_commander")

    turn_prompt = format_turn_prompt(
        turn_number=state["turn_number"],
        phase="Blue Force Planning",
        game_state=game_context,
        previous_actions=_format_recent_actions(state, "blue_commander"),
        objective="Analyze the current situation and recommend your next strategic move."
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=turn_prompt)
    ]

    # Get LLM response
    response = llm.invoke(messages)

    # Create action record
    action = AgentAction(
        agent="blue_commander",
        turn=state["turn_number"],
        action_type="strategic_recommendation",
        description=_extract_action_summary(response.content),
        grid_references=_extract_grid_references(response.content),
        units_involved=[],
        reasoning=response.content
    )

    # Update state
    new_actions = state["action_history"] + [action]

    return {
        "messages": [AIMessage(content=response.content, name="blue_commander")],
        "action_history": new_actions,
        "phase": "red_planning"
    }


def red_commander_node(state: GameState) -> dict:
    """
    Red Force Commander agent node.

    Provides adversarial perspective and counter-moves.
    """
    llm = create_llm()

    system_prompt = AgentPrompts.get_red_commander_prompt()
    game_context = format_game_state_for_agent(state, "red_commander")

    # Include Blue's last move for Red to respond to
    blue_last_action = _get_last_action(state, "blue_commander")

    turn_prompt = format_turn_prompt(
        turn_number=state["turn_number"],
        phase="Red Force Planning",
        game_state=game_context,
        previous_actions=f"Blue Force just executed: {blue_last_action}",
        objective="Counter Blue Force's move and advance Red Force objectives."
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=turn_prompt)
    ]

    response = llm.invoke(messages)

    action = AgentAction(
        agent="red_commander",
        turn=state["turn_number"],
        action_type="strategic_counter",
        description=_extract_action_summary(response.content),
        grid_references=_extract_grid_references(response.content),
        units_involved=[],
        reasoning=response.content
    )

    new_actions = state["action_history"] + [action]

    return {
        "messages": [AIMessage(content=response.content, name="red_commander")],
        "action_history": new_actions,
        "phase": "analysis"
    }


def analyst_node(state: GameState) -> dict:
    """
    Analyst agent node.

    Provides objective evaluation of both forces' decisions.
    """
    llm = create_llm()

    system_prompt = AgentPrompts.get_analyst_prompt()
    game_context = format_game_state_for_agent(state, "analyst")

    # Get both commanders' last actions
    blue_action = _get_last_action(state, "blue_commander")
    red_action = _get_last_action(state, "red_commander")

    turn_prompt = format_turn_prompt(
        turn_number=state["turn_number"],
        phase="Analysis",
        game_state=game_context,
        previous_actions=f"Blue: {blue_action}\n\nRed: {red_action}",
        objective="Evaluate both commanders' decisions and assess the strategic balance."
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=turn_prompt)
    ]

    response = llm.invoke(messages)

    # Extract evaluation scores from analyst response
    scores = _extract_evaluation_scores(response.content)

    action = AgentAction(
        agent="analyst",
        turn=state["turn_number"],
        action_type="evaluation",
        description="Strategic assessment completed",
        grid_references=[],
        units_involved=[],
        reasoning=response.content
    )

    new_actions = state["action_history"] + [action]

    # Update scores
    new_blue_scores = state["blue_scores"] + [scores.get("blue", {})]
    new_red_scores = state["red_scores"] + [scores.get("red", {})]

    return {
        "messages": [AIMessage(content=response.content, name="analyst")],
        "action_history": new_actions,
        "blue_scores": new_blue_scores,
        "red_scores": new_red_scores,
        "phase": "resolution",
        "turn_number": state["turn_number"] + 1
    }


def should_continue(state: GameState) -> Literal["continue", "end"]:
    """Determine if the simulation should continue or end."""
    # End conditions - use state's max_turns, default to 5 if not set
    max_turns = state.get("max_turns", 5)

    if state["turn_number"] > max_turns:
        return "end"

    if state["is_complete"]:
        return "end"

    # Check for decisive victory conditions
    blue_destroyed = all(u["status"] == "destroyed" for u in state["blue_units"])
    red_destroyed = all(u["status"] == "destroyed" for u in state["red_units"])

    if blue_destroyed or red_destroyed:
        return "end"

    return "continue"


def create_wargame_graph() -> StateGraph:
    """
    Create the LangGraph for wargaming simulation.

    Returns a compiled graph ready for execution.
    """
    # Initialize the graph with our state type
    graph = StateGraph(GameState)

    # Add nodes
    graph.add_node("blue_commander", blue_commander_node)
    graph.add_node("red_commander", red_commander_node)
    graph.add_node("analyst", analyst_node)

    # Set entry point
    graph.set_entry_point("blue_commander")

    # Add edges for the turn sequence
    graph.add_edge("blue_commander", "red_commander")
    graph.add_edge("red_commander", "analyst")

    # Conditional edge after analyst - continue or end
    graph.add_conditional_edges(
        "analyst",
        should_continue,
        {
            "continue": "blue_commander",
            "end": END
        }
    )

    return graph.compile()


async def run_simulation(
    initial_state: GameState,
    max_turns: int = 5,
    stream: bool = True
):
    """
    Run a wargaming simulation.

    Args:
        initial_state: The starting game state
        max_turns: Maximum number of turns to simulate
        stream: Whether to stream results as they come

    Yields:
        State updates as the simulation progresses
    """
    graph = create_wargame_graph()

    if stream:
        async for state in graph.astream(initial_state):
            yield state
    else:
        final_state = await graph.ainvoke(initial_state)
        yield final_state


# Helper functions

def _format_recent_actions(state: GameState, agent: str, limit: int = 3) -> str:
    """Format recent actions for context."""
    agent_actions = [a for a in state["action_history"] if a["agent"] == agent]
    recent = agent_actions[-limit:] if agent_actions else []

    if not recent:
        return "No previous actions this simulation."

    lines = []
    for action in recent:
        lines.append(f"Turn {action['turn']}: {action['description']}")

    return "\n".join(lines)


def _get_last_action(state: GameState, agent: str) -> str:
    """Get the last action taken by a specific agent."""
    agent_actions = [a for a in state["action_history"] if a["agent"] == agent]
    if agent_actions:
        return agent_actions[-1]["description"]
    return "No action yet"


def _extract_action_summary(content: str) -> str:
    """Extract a brief action summary from agent response."""
    # Look for the RECOMMENDED ACTION or STRATEGIC MOVE section
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if "RECOMMENDED ACTION" in line.upper() or "STRATEGIC MOVE" in line.upper():
            # Return the next non-empty line
            for next_line in lines[i + 1:i + 5]:
                if next_line.strip() and not next_line.startswith("#"):
                    return next_line.strip()[:200]

    # Fallback: return first substantive line
    for line in lines:
        if len(line.strip()) > 20 and not line.startswith("#"):
            return line.strip()[:200]

    return "Action recorded"


def _extract_grid_references(content: str) -> list[str]:
    """Extract military grid references from content."""
    import re
    # Pattern for grid references like XY-1234 or AB-5678
    pattern = r'[A-Z]{2}-\d{4}'
    matches = re.findall(pattern, content)
    return list(set(matches))


def _extract_evaluation_scores(content: str) -> dict:
    """Extract evaluation scores from analyst response."""
    import re

    scores = {"blue": {}, "red": {}}

    # Look for score patterns like "Geospatial Accuracy: 8/10" or "(8/10)"
    score_pattern = r'(\w+(?:\s+\w+)?)\s*[:\(]\s*(\d+(?:\.\d+)?)\s*(?:/10|/\d+|\))'

    # Simple extraction - in production, this would be more sophisticated
    lines = content.split("\n")
    current_force = None

    for line in lines:
        if "BLUE" in line.upper():
            current_force = "blue"
        elif "RED" in line.upper():
            current_force = "red"

        matches = re.findall(score_pattern, line, re.IGNORECASE)
        for metric, score in matches:
            if current_force:
                scores[current_force][metric.lower().replace(" ", "_")] = float(score)

    return scores
