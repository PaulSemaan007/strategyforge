"""
Geospatial distance calculations for StrategyForge.

Provides accurate distance and bearing calculations using the
Haversine formula for great-circle distances on Earth.
"""

import math
from typing import Tuple

# Earth's radius in kilometers
EARTH_RADIUS_KM = 6371.0


def calculate_distance(
    from_position: Tuple[float, float],
    to_position: Tuple[float, float]
) -> float:
    """
    Calculate the great-circle distance between two points using Haversine formula.

    Args:
        from_position: (latitude, longitude) of starting point
        to_position: (latitude, longitude) of ending point

    Returns:
        Distance in kilometers

    Example:
        >>> calculate_distance((25.0, 121.0), (24.5, 119.5))
        168.5  # Approximate distance across Taiwan Strait
    """
    lat1, lon1 = from_position
    lat2, lon2 = to_position

    # Convert to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    # Haversine formula
    a = (
        math.sin(delta_lat / 2) ** 2 +
        math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = EARTH_RADIUS_KM * c
    return round(distance, 2)


def calculate_bearing(
    from_position: Tuple[float, float],
    to_position: Tuple[float, float]
) -> float:
    """
    Calculate the initial bearing from one point to another.

    Args:
        from_position: (latitude, longitude) of starting point
        to_position: (latitude, longitude) of ending point

    Returns:
        Bearing in degrees (0-360, where 0 = North)

    Example:
        >>> calculate_bearing((25.0, 121.0), (24.5, 119.5))
        245.3  # Southwest bearing
    """
    lat1, lon1 = from_position
    lat2, lon2 = to_position

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lon = math.radians(lon2 - lon1)

    x = math.sin(delta_lon) * math.cos(lat2_rad)
    y = (
        math.cos(lat1_rad) * math.sin(lat2_rad) -
        math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon)
    )

    bearing_rad = math.atan2(x, y)
    bearing_deg = math.degrees(bearing_rad)

    # Normalize to 0-360
    bearing = (bearing_deg + 360) % 360
    return round(bearing, 1)


def calculate_midpoint(
    from_position: Tuple[float, float],
    to_position: Tuple[float, float]
) -> Tuple[float, float]:
    """
    Calculate the midpoint between two positions.

    Args:
        from_position: (latitude, longitude) of first point
        to_position: (latitude, longitude) of second point

    Returns:
        (latitude, longitude) of midpoint
    """
    lat1, lon1 = from_position
    lat2, lon2 = to_position

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lon = math.radians(lon2 - lon1)

    bx = math.cos(lat2_rad) * math.cos(delta_lon)
    by = math.cos(lat2_rad) * math.sin(delta_lon)

    lat_mid = math.atan2(
        math.sin(lat1_rad) + math.sin(lat2_rad),
        math.sqrt((math.cos(lat1_rad) + bx) ** 2 + by ** 2)
    )
    lon_mid = math.radians(lon1) + math.atan2(by, math.cos(lat1_rad) + bx)

    return (round(math.degrees(lat_mid), 4), round(math.degrees(lon_mid), 4))


def estimate_travel_time(
    distance_km: float,
    speed_kmh: float
) -> float:
    """
    Estimate travel time for a unit.

    Args:
        distance_km: Distance to travel in kilometers
        speed_kmh: Speed in kilometers per hour

    Returns:
        Travel time in hours
    """
    if speed_kmh <= 0:
        return float('inf')
    return round(distance_km / speed_kmh, 2)


def is_within_range(
    unit_position: Tuple[float, float],
    target_position: Tuple[float, float],
    range_km: float
) -> bool:
    """
    Check if a target is within a unit's operational range.

    Args:
        unit_position: (lat, lon) of the unit
        target_position: (lat, lon) of the target
        range_km: Maximum range in kilometers

    Returns:
        True if target is within range
    """
    distance = calculate_distance(unit_position, target_position)
    return distance <= range_km


def cardinal_direction(bearing: float) -> str:
    """
    Convert bearing to cardinal direction.

    Args:
        bearing: Bearing in degrees (0-360)

    Returns:
        Cardinal direction (N, NE, E, SE, S, SW, W, NW)
    """
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    index = round(bearing / 45) % 8
    return directions[index]


# Convenience functions for scenario-specific calculations
def taiwan_strait_width() -> float:
    """
    Calculate the approximate width of Taiwan Strait at its narrowest.

    Returns:
        Width in kilometers (approximately 130km at narrowest)
    """
    # Approximate coordinates for narrowest crossing
    mainland = (24.45, 118.1)  # Fujian coast
    taiwan = (24.45, 120.2)    # Taiwan west coast

    return calculate_distance(mainland, taiwan)


if __name__ == "__main__":
    # Demo calculations
    print("StrategyForge Geospatial Demo\n")

    # Taiwan Strait calculations
    taipei = (25.0330, 121.5654)
    xiamen = (24.4798, 118.0894)

    dist = calculate_distance(taipei, xiamen)
    bearing = calculate_bearing(taipei, xiamen)
    direction = cardinal_direction(bearing)

    print(f"Taipei to Xiamen:")
    print(f"  Distance: {dist} km")
    print(f"  Bearing: {bearing}° ({direction})")
    print(f"  Fighter transit (Mach 1.5): {estimate_travel_time(dist, 1800):.1f} hours")
    print(f"  Naval transit (30 knots): {estimate_travel_time(dist, 55):.1f} hours")

    print(f"\nTaiwan Strait width: {taiwan_strait_width():.1f} km")
