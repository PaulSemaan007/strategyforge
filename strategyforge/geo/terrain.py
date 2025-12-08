"""
Terrain analysis for StrategyForge.

Provides terrain type classification and analysis for
military planning purposes.
"""

from dataclasses import dataclass
from typing import Tuple, Literal


@dataclass
class TerrainInfo:
    """Information about terrain at a location."""
    terrain_type: str
    elevation_m: float
    defensibility: int  # 1-10 scale
    cover: int  # 1-10 scale
    mobility: int  # 1-10 scale (higher = easier movement)
    description: str


class TerrainAnalyzer:
    """
    Analyzes terrain characteristics for military planning.

    Uses simplified heuristics based on coordinates.
    In production, this would query actual terrain databases.
    """

    # Taiwan Strait region terrain definitions
    TERRAIN_REGIONS = {
        "mainland_coast": {
            "bounds": {"lat": (22.0, 26.0), "lon": (117.0, 119.0)},
            "type": "coastal",
            "elevation": 50,
            "defensibility": 7,
            "cover": 6,
            "mobility": 7,
            "description": "Coastal mainland with port infrastructure and air bases"
        },
        "taiwan_strait": {
            "bounds": {"lat": (22.5, 26.0), "lon": (119.0, 120.5)},
            "type": "water",
            "elevation": 0,
            "defensibility": 2,
            "cover": 1,
            "mobility": 8,
            "description": "Open water, average depth 60m, heavy shipping traffic"
        },
        "taiwan_west": {
            "bounds": {"lat": (22.0, 25.5), "lon": (120.0, 121.0)},
            "type": "coastal_urban",
            "elevation": 100,
            "defensibility": 8,
            "cover": 7,
            "mobility": 6,
            "description": "Narrow coastal plain with urban density"
        },
        "taiwan_mountains": {
            "bounds": {"lat": (22.5, 25.5), "lon": (121.0, 122.0)},
            "type": "mountain",
            "elevation": 2000,
            "defensibility": 9,
            "cover": 8,
            "mobility": 3,
            "description": "Central mountain range, heavily forested"
        },
        "taiwan_east": {
            "bounds": {"lat": (22.0, 25.0), "lon": (121.0, 122.0)},
            "type": "coastal_mountain",
            "elevation": 500,
            "defensibility": 8,
            "cover": 7,
            "mobility": 4,
            "description": "Eastern coast with cliffs and limited beaches"
        }
    }

    def analyze(self, lat: float, lon: float) -> TerrainInfo:
        """
        Analyze terrain at a given position.

        Args:
            lat: Latitude
            lon: Longitude

        Returns:
            TerrainInfo with terrain characteristics
        """
        # Find matching region
        for region_name, region in self.TERRAIN_REGIONS.items():
            bounds = region["bounds"]
            if (bounds["lat"][0] <= lat <= bounds["lat"][1] and
                bounds["lon"][0] <= lon <= bounds["lon"][1]):
                return TerrainInfo(
                    terrain_type=region["type"],
                    elevation_m=region["elevation"],
                    defensibility=region["defensibility"],
                    cover=region["cover"],
                    mobility=region["mobility"],
                    description=region["description"]
                )

        # Default for areas outside defined regions
        return TerrainInfo(
            terrain_type="unknown",
            elevation_m=0,
            defensibility=5,
            cover=5,
            mobility=5,
            description="Area outside primary scenario bounds"
        )

    def get_defensive_value(self, lat: float, lon: float) -> int:
        """Get defensive value of terrain (1-10)."""
        return self.analyze(lat, lon).defensibility

    def get_mobility_factor(self, lat: float, lon: float) -> float:
        """Get mobility factor (0.1-1.0) affecting movement speed."""
        mobility = self.analyze(lat, lon).mobility
        return mobility / 10.0

    def is_water(self, lat: float, lon: float) -> bool:
        """Check if position is over water."""
        return self.analyze(lat, lon).terrain_type == "water"

    def is_urban(self, lat: float, lon: float) -> bool:
        """Check if position is in urban area."""
        terrain_type = self.analyze(lat, lon).terrain_type
        return "urban" in terrain_type

    def compare_positions(
        self,
        pos1: Tuple[float, float],
        pos2: Tuple[float, float]
    ) -> dict:
        """
        Compare terrain advantage between two positions.

        Returns dict with comparison metrics.
        """
        terrain1 = self.analyze(pos1[0], pos1[1])
        terrain2 = self.analyze(pos2[0], pos2[1])

        return {
            "position_1": {
                "terrain": terrain1.terrain_type,
                "defensibility": terrain1.defensibility,
                "cover": terrain1.cover
            },
            "position_2": {
                "terrain": terrain2.terrain_type,
                "defensibility": terrain2.defensibility,
                "cover": terrain2.cover
            },
            "defensive_advantage": terrain1.defensibility - terrain2.defensibility,
            "cover_advantage": terrain1.cover - terrain2.cover,
            "assessment": _assess_advantage(
                terrain1.defensibility - terrain2.defensibility
            )
        }


def _assess_advantage(diff: int) -> str:
    """Convert numeric advantage to text assessment."""
    if diff >= 3:
        return "Strong advantage to position 1"
    elif diff >= 1:
        return "Slight advantage to position 1"
    elif diff <= -3:
        return "Strong advantage to position 2"
    elif diff <= -1:
        return "Slight advantage to position 2"
    else:
        return "Positions roughly equivalent"
