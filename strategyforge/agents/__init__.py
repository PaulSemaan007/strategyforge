"""
Agent system for StrategyForge wargaming simulation.

This module contains the LangGraph-based multi-agent system that
powers the wargaming simulation, including:
- Blue Force Commander (friendly forces)
- Red Force Commander (adversary)
- Analyst Agent (neutral assessment)
"""

from .graph import create_wargame_graph, run_simulation
from .prompts import AgentPrompts

__all__ = ["create_wargame_graph", "run_simulation", "AgentPrompts"]
