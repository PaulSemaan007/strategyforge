"""
Geospatial utilities for StrategyForge.

Provides geospatial analysis capabilities:
- Distance calculations (haversine, geodesic)
- Terrain analysis
- Map visualization with Folium
"""

from .distance import calculate_distance, calculate_bearing
from .terrain import TerrainAnalyzer

__all__ = ["calculate_distance", "calculate_bearing", "TerrainAnalyzer"]
