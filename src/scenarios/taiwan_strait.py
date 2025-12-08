"""
Taiwan Strait Crisis Scenario.

A realistic Indo-Pacific scenario demonstrating geospatial reasoning
and multi-domain military operations. This scenario is designed to
showcase LLM capabilities in understanding:
- Maritime chokepoints and sea control
- Air defense zones and no-fly areas
- Amphibious operations considerations
- Strategic distance and time calculations

Note: This is a fictional training scenario for AI evaluation purposes.
"""

from .base import Scenario, Force, Unit, Position, Objective


class TaiwanStraitScenario(Scenario):
    """
    Taiwan Strait crisis scenario for wargaming evaluation.

    Geographic Context:
    - Taiwan Strait: ~180km wide at narrowest point
    - Key positions: Taiwan (Blue), Mainland coast (Red)
    - Critical chokepoints and sea lanes

    This scenario tests LLM ability to:
    1. Correctly calculate maritime distances
    2. Understand terrain/water barriers
    3. Reason about air and naval domains
    4. Anticipate adversarial moves
    """

    def __init__(self):
        super().__init__(
            name="Taiwan Strait Crisis",
            description="Multi-domain conflict scenario in the Taiwan Strait region. "
                        "Blue Force defends island positions while Red Force seeks to "
                        "establish sea and air control."
        )
        self.setup()

    def setup(self) -> None:
        """Initialize the Taiwan Strait scenario."""

        # Set geographic bounds (approximate)
        self.bounds = {
            "north": 26.0,
            "south": 22.0,
            "east": 122.5,
            "west": 117.0
        }

        # === BLUE FORCE (Defensive) ===
        self.blue_force = Force(name="Blue Force - Island Defense", side="blue")

        # Air assets
        self.blue_force.add_unit(Unit(
            id="blue_air_1",
            name="1st Fighter Wing",
            type="air",
            force="blue",
            position=Position(lat=25.0777, lon=121.2325, grid_ref="TW-1001"),
            capabilities=["air_superiority", "intercept", "patrol"],
            range_km=800,
            speed_kmh=2400
        ))

        self.blue_force.add_unit(Unit(
            id="blue_air_2",
            name="2nd Fighter Wing",
            type="air",
            force="blue",
            position=Position(lat=22.6727, lon=120.4618, grid_ref="TW-2001"),
            capabilities=["air_superiority", "ground_attack"],
            range_km=750,
            speed_kmh=2200
        ))

        self.blue_force.add_unit(Unit(
            id="blue_awacs_1",
            name="Early Warning Squadron",
            type="air",
            force="blue",
            position=Position(lat=24.0, lon=121.5, grid_ref="TW-1500"),
            capabilities=["early_warning", "command_control", "surveillance"],
            range_km=500,
            speed_kmh=850
        ))

        # Naval assets
        self.blue_force.add_unit(Unit(
            id="blue_naval_1",
            name="Destroyer Squadron 1",
            type="naval",
            force="blue",
            position=Position(lat=24.5, lon=120.0, grid_ref="TS-3001"),
            capabilities=["anti_air", "anti_surface", "missile_defense"],
            range_km=300,
            speed_kmh=55
        ))

        self.blue_force.add_unit(Unit(
            id="blue_naval_2",
            name="Frigate Group Alpha",
            type="naval",
            force="blue",
            position=Position(lat=23.5, lon=119.5, grid_ref="TS-4001"),
            capabilities=["anti_submarine", "patrol", "escort"],
            range_km=250,
            speed_kmh=50
        ))

        self.blue_force.add_unit(Unit(
            id="blue_sub_1",
            name="Submarine Division 1",
            type="naval",
            force="blue",
            position=Position(lat=24.0, lon=119.0, grid_ref="TS-5001"),
            capabilities=["anti_surface", "reconnaissance", "mine_laying"],
            range_km=400,
            speed_kmh=40
        ))

        # Ground/coastal defense
        self.blue_force.add_unit(Unit(
            id="blue_ground_1",
            name="Coastal Defense Battery 1",
            type="ground",
            force="blue",
            position=Position(lat=25.1, lon=121.4, grid_ref="TW-1010"),
            capabilities=["anti_ship_missile", "coastal_defense"],
            range_km=150,
            speed_kmh=0
        ))

        self.blue_force.add_unit(Unit(
            id="blue_ground_2",
            name="SAM Battery Alpha",
            type="ground",
            force="blue",
            position=Position(lat=24.5, lon=120.8, grid_ref="TW-1500"),
            capabilities=["air_defense", "missile_intercept"],
            range_km=200,
            speed_kmh=0
        ))

        # Blue force resources
        self.blue_force.resources = {
            "aircraft": 120,
            "missiles": 500,
            "fuel_days": 30,
            "ammunition_days": 45
        }

        # === RED FORCE (Offensive) ===
        self.red_force = Force(name="Red Force - Maritime Offensive", side="red")

        # Air assets
        self.red_force.add_unit(Unit(
            id="red_air_1",
            name="1st Attack Wing",
            type="air",
            force="red",
            position=Position(lat=25.5, lon=119.0, grid_ref="ML-1001"),
            capabilities=["air_superiority", "strike", "escort"],
            range_km=1200,
            speed_kmh=2500
        ))

        self.red_force.add_unit(Unit(
            id="red_air_2",
            name="2nd Bomber Wing",
            type="air",
            force="red",
            position=Position(lat=26.0, lon=119.5, grid_ref="ML-0501"),
            capabilities=["anti_ship", "strike", "standoff_attack"],
            range_km=3000,
            speed_kmh=900
        ))

        self.red_force.add_unit(Unit(
            id="red_air_3",
            name="Electronic Warfare Squadron",
            type="air",
            force="red",
            position=Position(lat=25.0, lon=118.5, grid_ref="ML-2001"),
            capabilities=["jamming", "elint", "suppression"],
            range_km=600,
            speed_kmh=800
        ))

        # Naval assets
        self.red_force.add_unit(Unit(
            id="red_naval_1",
            name="Carrier Strike Group",
            type="naval",
            force="red",
            position=Position(lat=24.0, lon=118.0, grid_ref="EC-1001"),
            capabilities=["power_projection", "air_ops", "command"],
            range_km=500,
            speed_kmh=55
        ))

        self.red_force.add_unit(Unit(
            id="red_naval_2",
            name="Amphibious Ready Group",
            type="naval",
            force="red",
            position=Position(lat=24.5, lon=118.5, grid_ref="EC-2001"),
            capabilities=["amphibious_assault", "transport", "fire_support"],
            range_km=300,
            speed_kmh=35
        ))

        self.red_force.add_unit(Unit(
            id="red_naval_3",
            name="Destroyer Squadron East",
            type="naval",
            force="red",
            position=Position(lat=25.0, lon=118.0, grid_ref="EC-0501"),
            capabilities=["anti_air", "anti_surface", "land_attack"],
            range_km=350,
            speed_kmh=55
        ))

        self.red_force.add_unit(Unit(
            id="red_sub_1",
            name="Attack Submarine Division",
            type="naval",
            force="red",
            position=Position(lat=23.5, lon=118.0, grid_ref="EC-3001"),
            capabilities=["anti_surface", "anti_submarine", "reconnaissance"],
            range_km=500,
            speed_kmh=45
        ))

        # Ground/missile forces
        self.red_force.add_unit(Unit(
            id="red_ground_1",
            name="Rocket Force Brigade 1",
            type="ground",
            force="red",
            position=Position(lat=26.0, lon=118.0, grid_ref="ML-0001"),
            capabilities=["ballistic_missile", "cruise_missile", "strike"],
            range_km=1500,
            speed_kmh=0
        ))

        # Red force resources
        self.red_force.resources = {
            "aircraft": 400,
            "missiles": 1500,
            "fuel_days": 60,
            "ammunition_days": 90
        }

        # === OBJECTIVES ===
        self.objectives = [
            Objective(
                id="obj_strait_control",
                name="Strait Control",
                description="Establish sea control over Taiwan Strait shipping lanes",
                position=Position(lat=24.5, lon=119.5, grid_ref="TS-0000"),
                owner="contested",
                value=10
            ),
            Objective(
                id="obj_air_superiority",
                name="Air Superiority Zone",
                description="Achieve air superiority over the operational area",
                position=Position(lat=24.0, lon=120.0, grid_ref="AS-0000"),
                owner="contested",
                value=9
            ),
            Objective(
                id="obj_port_access",
                name="Port Access",
                description="Maintain/deny access to major port facilities",
                position=Position(lat=25.0, lon=121.5, grid_ref="PT-0001"),
                owner="blue",
                value=8
            ),
            Objective(
                id="obj_early_warning",
                name="Early Warning Network",
                description="Maintain/suppress early warning radar coverage",
                position=Position(lat=24.5, lon=121.0, grid_ref="EW-0001"),
                owner="blue",
                value=7
            )
        ]

        # Terrain data for the region
        self.terrain_data = {
            "taiwan_strait": {
                "type": "water",
                "width_km": 180,
                "depth_avg_m": 60,
                "current_knots": 2.5,
                "description": "Shallow strait with significant shipping traffic"
            },
            "taiwan_west_coast": {
                "type": "coastal",
                "beach_km": 40,
                "defensible": True,
                "description": "Limited suitable landing beaches, urban density"
            },
            "mainland_coast": {
                "type": "coastal",
                "port_capacity": "high",
                "air_bases": 12,
                "description": "Extensive military infrastructure"
            }
        }


def create_demo_scenario() -> TaiwanStraitScenario:
    """Create and return the Taiwan Strait demo scenario."""
    return TaiwanStraitScenario()
