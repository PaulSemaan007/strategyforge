"""
Agent tools for StrategyForge.

Provides tools that agents can use during simulation:
- Geospatial tools (distance, terrain analysis)
- Intelligence tools (reconnaissance, intel gathering)
- Resource tools (logistics, supply tracking)
"""

from .geospatial import (
    GEOSPATIAL_TOOLS,
    get_distance,
    check_weapon_range,
    analyze_terrain,
    estimate_force_transit,
)

__all__ = [
    "GEOSPATIAL_TOOLS",
    "get_distance",
    "check_weapon_range",
    "analyze_terrain",
    "estimate_force_transit",
]
