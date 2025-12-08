"""
Geospatial tools for LLM agents.

These tools are provided to agents so they can make accurate
geospatial calculations rather than hallucinating distances.
"""

from typing import Literal
from langchain_core.tools import tool

from ..geo.distance import (
    calculate_distance,
    calculate_bearing,
    is_within_range,
    estimate_travel_time,
    cardinal_direction
)


@tool
def get_distance(
    from_lat: float,
    from_lon: float,
    to_lat: float,
    to_lon: float
) -> str:
    """
    Calculate the distance between two geographic positions.

    Use this tool to get accurate distances rather than estimating.
    Distances are calculated using great-circle (Haversine) formula.

    Args:
        from_lat: Latitude of starting position
        from_lon: Longitude of starting position
        to_lat: Latitude of destination
        to_lon: Longitude of destination

    Returns:
        Distance information including kilometers and bearing
    """
    dist = calculate_distance((from_lat, from_lon), (to_lat, to_lon))
    bearing = calculate_bearing((from_lat, from_lon), (to_lat, to_lon))
    direction = cardinal_direction(bearing)

    return (
        f"Distance: {dist} km\n"
        f"Bearing: {bearing}° ({direction})\n"
        f"Air transit (800 km/h): {estimate_travel_time(dist, 800):.1f} hours\n"
        f"Naval transit (50 km/h): {estimate_travel_time(dist, 50):.1f} hours\n"
        f"Ground transit (60 km/h): {estimate_travel_time(dist, 60):.1f} hours"
    )


@tool
def check_weapon_range(
    unit_lat: float,
    unit_lon: float,
    target_lat: float,
    target_lon: float,
    weapon_range_km: float
) -> str:
    """
    Check if a target is within a weapon system's range.

    Use this to determine if units can engage targets from current positions.

    Args:
        unit_lat: Latitude of the firing unit
        unit_lon: Longitude of the firing unit
        target_lat: Latitude of the target
        target_lon: Longitude of the target
        weapon_range_km: Maximum range of the weapon in kilometers

    Returns:
        Whether target is in range and distance details
    """
    in_range = is_within_range(
        (unit_lat, unit_lon),
        (target_lat, target_lon),
        weapon_range_km
    )
    dist = calculate_distance((unit_lat, unit_lon), (target_lat, target_lon))

    if in_range:
        margin = weapon_range_km - dist
        return (
            f"TARGET IN RANGE\n"
            f"Distance to target: {dist} km\n"
            f"Weapon range: {weapon_range_km} km\n"
            f"Range margin: {margin:.1f} km"
        )
    else:
        shortfall = dist - weapon_range_km
        return (
            f"TARGET OUT OF RANGE\n"
            f"Distance to target: {dist} km\n"
            f"Weapon range: {weapon_range_km} km\n"
            f"Range shortfall: {shortfall:.1f} km\n"
            f"Unit must close {shortfall:.1f} km to engage"
        )


@tool
def analyze_terrain(
    lat: float,
    lon: float,
    analysis_type: Literal["tactical", "strategic"] = "tactical"
) -> str:
    """
    Analyze terrain characteristics at a position.

    Provides terrain information for tactical and strategic planning.

    Args:
        lat: Latitude of position
        lon: Longitude of position
        analysis_type: Level of analysis detail

    Returns:
        Terrain analysis including type, defensibility, and considerations
    """
    # Simplified terrain analysis based on coordinates
    # In production, this would query actual terrain data

    # Taiwan Strait region heuristics
    if 117.0 <= lon <= 122.5 and 22.0 <= lat <= 26.0:
        if lon < 119.0:
            terrain_type = "mainland_coast"
            terrain_desc = (
                "Coastal mainland with extensive port infrastructure.\n"
                "Multiple air bases within 200km.\n"
                "Strong defensive positions with layered air defense."
            )
        elif lon < 120.5:
            terrain_type = "taiwan_strait"
            terrain_desc = (
                "Open water, average depth 60m.\n"
                "Heavy commercial shipping traffic.\n"
                "Limited concealment for naval forces.\n"
                "Strong currents (2-3 knots)."
            )
        else:
            terrain_type = "taiwan_coast"
            terrain_desc = (
                "Mountainous terrain rising from narrow coastal plain.\n"
                "Limited suitable amphibious landing beaches.\n"
                "Urban density provides defensive advantage.\n"
                "Pre-positioned coastal defense systems."
            )

        if analysis_type == "strategic":
            terrain_desc += (
                "\n\nSTRATEGIC CONSIDERATIONS:\n"
                "- Strait width ~180km at narrowest\n"
                "- Air transit time: 10-15 minutes\n"
                "- Naval transit time: 3-4 hours\n"
                "- Limited sea state windows for amphibious ops"
            )

        return f"Terrain Type: {terrain_type}\n\n{terrain_desc}"

    return (
        "Position outside primary scenario bounds.\n"
        "Generic terrain analysis: Mixed terrain, standard considerations apply."
    )


@tool
def estimate_force_transit(
    force_type: Literal["air", "naval", "ground"],
    from_lat: float,
    from_lon: float,
    to_lat: float,
    to_lon: float
) -> str:
    """
    Estimate transit time for a force type between two positions.

    Accounts for typical speeds and operational considerations.

    Args:
        force_type: Type of force (air, naval, ground)
        from_lat: Starting latitude
        from_lon: Starting longitude
        to_lat: Destination latitude
        to_lon: Destination longitude

    Returns:
        Transit time estimates with operational notes
    """
    dist = calculate_distance((from_lat, from_lon), (to_lat, to_lon))
    bearing = calculate_bearing((from_lat, from_lon), (to_lat, to_lon))
    direction = cardinal_direction(bearing)

    speeds = {
        "air": {"fast": 2000, "cruise": 800, "slow": 400},
        "naval": {"fast": 55, "cruise": 35, "slow": 20},
        "ground": {"fast": 80, "cruise": 50, "slow": 30}
    }

    s = speeds[force_type]

    result = [
        f"Force Type: {force_type.upper()}",
        f"Distance: {dist} km ({direction})",
        "",
        "Transit Time Estimates:",
        f"  Fast: {estimate_travel_time(dist, s['fast']):.1f} hours",
        f"  Cruise: {estimate_travel_time(dist, s['cruise']):.1f} hours",
        f"  Slow/Cautious: {estimate_travel_time(dist, s['slow']):.1f} hours",
    ]

    if force_type == "air":
        result.append("\nNote: Does not include loiter time or refueling requirements")
    elif force_type == "naval":
        result.append("\nNote: Assumes favorable sea state; storms may delay 2-3x")
    else:
        result.append("\nNote: Terrain and road conditions may significantly affect speed")

    return "\n".join(result)


# Export tools for agent use
GEOSPATIAL_TOOLS = [
    get_distance,
    check_weapon_range,
    analyze_terrain,
    estimate_force_transit
]


def get_tool_descriptions() -> str:
    """Get formatted descriptions of all geospatial tools."""
    lines = ["Available Geospatial Tools:\n"]
    for tool in GEOSPATIAL_TOOLS:
        lines.append(f"- {tool.name}: {tool.description.split(chr(10))[0]}")
    return "\n".join(lines)
