"""
Base scenario definitions for StrategyForge.

Scenarios define the initial conditions, forces, terrain, and objectives
for wargaming simulations. This module provides the base classes and
utilities for creating and managing scenarios.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Literal
import json
from pathlib import Path


@dataclass
class Position:
    """Geographic position with coordinates and military grid reference."""
    lat: float
    lon: float
    grid_ref: str = ""

    def to_dict(self) -> dict:
        return {"lat": self.lat, "lon": self.lon, "grid_ref": self.grid_ref}

    @classmethod
    def from_dict(cls, data: dict) -> "Position":
        return cls(
            lat=data["lat"],
            lon=data["lon"],
            grid_ref=data.get("grid_ref", "")
        )

    def __str__(self) -> str:
        if self.grid_ref:
            return f"{self.grid_ref} ({self.lat:.4f}, {self.lon:.4f})"
        return f"({self.lat:.4f}, {self.lon:.4f})"


@dataclass
class Unit:
    """
    A military unit in the simulation.

    Units are the basic elements that agents command and maneuver.
    """
    id: str
    name: str
    type: Literal["air", "naval", "ground", "cyber", "space"]
    force: Literal["blue", "red"]
    position: Position
    status: Literal["ready", "engaged", "damaged", "destroyed"] = "ready"
    capabilities: list[str] = field(default_factory=list)
    range_km: float = 0  # Operational range
    speed_kmh: float = 0  # Movement speed

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "force": self.force,
            "position": self.position.to_dict(),
            "status": self.status,
            "capabilities": self.capabilities,
            "range_km": self.range_km,
            "speed_kmh": self.speed_kmh
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Unit":
        return cls(
            id=data["id"],
            name=data["name"],
            type=data["type"],
            force=data["force"],
            position=Position.from_dict(data["position"]),
            status=data.get("status", "ready"),
            capabilities=data.get("capabilities", []),
            range_km=data.get("range_km", 0),
            speed_kmh=data.get("speed_kmh", 0)
        )


@dataclass
class Objective:
    """A strategic objective in the scenario."""
    id: str
    name: str
    description: str
    position: Position
    owner: Literal["blue", "red", "contested", "neutral"]
    value: int  # Strategic importance (1-10)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "position": self.position.to_dict(),
            "owner": self.owner,
            "value": self.value
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Objective":
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            position=Position.from_dict(data["position"]),
            owner=data.get("owner", "neutral"),
            value=data.get("value", 5)
        )


@dataclass
class Force:
    """A collection of units belonging to one side."""
    name: str
    side: Literal["blue", "red"]
    units: list[Unit] = field(default_factory=list)
    resources: dict = field(default_factory=dict)

    def add_unit(self, unit: Unit) -> None:
        """Add a unit to the force."""
        unit.force = self.side
        self.units.append(unit)

    def get_units_by_type(self, unit_type: str) -> list[Unit]:
        """Get all units of a specific type."""
        return [u for u in self.units if u.type == unit_type]

    def get_active_units(self) -> list[Unit]:
        """Get all non-destroyed units."""
        return [u for u in self.units if u.status != "destroyed"]

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "side": self.side,
            "units": [u.to_dict() for u in self.units],
            "resources": self.resources
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Force":
        force = cls(
            name=data["name"],
            side=data["side"],
            resources=data.get("resources", {})
        )
        for unit_data in data.get("units", []):
            force.units.append(Unit.from_dict(unit_data))
        return force


class Scenario(ABC):
    """
    Abstract base class for wargaming scenarios.

    A scenario defines:
    - The geographic area of operations
    - Initial force dispositions
    - Strategic objectives
    - Victory conditions
    - Terrain and environmental factors
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.blue_force: Force = Force(name="Blue Force", side="blue")
        self.red_force: Force = Force(name="Red Force", side="red")
        self.objectives: list[Objective] = []
        self.terrain_data: dict = {}
        self.bounds: dict = {}  # Geographic bounds of the scenario

    @abstractmethod
    def setup(self) -> None:
        """Initialize the scenario with forces, objectives, and terrain."""
        pass

    def get_initial_state(self) -> dict:
        """Convert scenario to initial game state."""
        from ..agents.state import GameState, create_initial_state

        return create_initial_state(
            scenario_name=self.name,
            blue_units=[u.to_dict() for u in self.blue_force.units],
            red_units=[u.to_dict() for u in self.red_force.units],
            objectives={obj.id: obj.to_dict() for obj in self.objectives},
            terrain_data=self.terrain_data
        )

    def to_dict(self) -> dict:
        """Serialize scenario to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "blue_force": self.blue_force.to_dict(),
            "red_force": self.red_force.to_dict(),
            "objectives": [o.to_dict() for o in self.objectives],
            "terrain_data": self.terrain_data,
            "bounds": self.bounds
        }

    def save(self, path: Path) -> None:
        """Save scenario to JSON file."""
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: Path) -> "Scenario":
        """Load scenario from JSON file."""
        with open(path, "r") as f:
            data = json.load(f)

        # Create a generic scenario from loaded data
        scenario = GenericScenario(
            name=data["name"],
            description=data["description"]
        )
        scenario.blue_force = Force.from_dict(data["blue_force"])
        scenario.red_force = Force.from_dict(data["red_force"])
        scenario.objectives = [Objective.from_dict(o) for o in data.get("objectives", [])]
        scenario.terrain_data = data.get("terrain_data", {})
        scenario.bounds = data.get("bounds", {})

        return scenario

    def summary(self) -> str:
        """Get a human-readable summary of the scenario."""
        lines = [
            f"Scenario: {self.name}",
            f"Description: {self.description}",
            "",
            f"Blue Force: {len(self.blue_force.units)} units",
        ]

        for unit_type in ["air", "naval", "ground"]:
            count = len(self.blue_force.get_units_by_type(unit_type))
            if count > 0:
                lines.append(f"  - {unit_type.capitalize()}: {count}")

        lines.append(f"\nRed Force: {len(self.red_force.units)} units")

        for unit_type in ["air", "naval", "ground"]:
            count = len(self.red_force.get_units_by_type(unit_type))
            if count > 0:
                lines.append(f"  - {unit_type.capitalize()}: {count}")

        lines.append(f"\nObjectives: {len(self.objectives)}")
        for obj in self.objectives:
            lines.append(f"  - {obj.name} ({obj.owner}): {obj.description}")

        return "\n".join(lines)


class GenericScenario(Scenario):
    """A generic scenario loaded from configuration."""

    def setup(self) -> None:
        """No-op for generic scenarios loaded from files."""
        pass
