"""
Map visualization for StrategyForge wargaming simulations.

Uses Folium to create interactive maps showing:
- Force positions (Blue/Red units)
- Strategic objectives
- Movement paths
- Terrain features
"""

import folium
from folium import plugins
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class MapConfig:
    """Configuration for map visualization."""
    center_lat: float = 24.5
    center_lon: float = 120.0
    zoom_start: int = 7
    tiles: str = "CartoDB positron"


# Unit type icons (using Font Awesome via folium)
UNIT_ICONS = {
    "air": {"icon": "plane", "prefix": "fa"},
    "naval": {"icon": "ship", "prefix": "fa"},
    "ground": {"icon": "shield", "prefix": "fa"},
    "cyber": {"icon": "laptop", "prefix": "fa"},
    "space": {"icon": "satellite", "prefix": "fa"},
}

# Force colors
FORCE_COLORS = {
    "blue": "#2563eb",  # Blue
    "red": "#dc2626",   # Red
}

OBJECTIVE_COLOR = "#f59e0b"  # Amber


def create_scenario_map(
    scenario,
    config: Optional[MapConfig] = None,
    show_ranges: bool = False,
    show_grid: bool = True
) -> folium.Map:
    """
    Create an interactive Folium map for a wargaming scenario.

    Args:
        scenario: A Scenario object with forces and objectives
        config: Map configuration (optional)
        show_ranges: Whether to show unit operational ranges
        show_grid: Whether to show a coordinate grid

    Returns:
        A Folium Map object
    """
    config = config or MapConfig()

    # Create base map
    m = folium.Map(
        location=[config.center_lat, config.center_lon],
        zoom_start=config.zoom_start,
        tiles=config.tiles
    )

    # Add alternative tile layers
    folium.TileLayer("OpenStreetMap", name="Street Map").add_to(m)
    folium.TileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri",
        name="Satellite"
    ).add_to(m)

    # Create feature groups for layers
    blue_layer = folium.FeatureGroup(name="Blue Forces")
    red_layer = folium.FeatureGroup(name="Red Forces")
    objectives_layer = folium.FeatureGroup(name="Objectives")
    ranges_layer = folium.FeatureGroup(name="Weapon Ranges", show=False)

    # Add Blue Force units
    for unit in scenario.blue_force.units:
        _add_unit_marker(blue_layer, unit, "blue", show_ranges, ranges_layer)

    # Add Red Force units
    for unit in scenario.red_force.units:
        _add_unit_marker(red_layer, unit, "red", show_ranges, ranges_layer)

    # Add objectives
    for obj in scenario.objectives:
        _add_objective_marker(objectives_layer, obj)

    # Add layers to map
    blue_layer.add_to(m)
    red_layer.add_to(m)
    objectives_layer.add_to(m)
    ranges_layer.add_to(m)

    # Add Taiwan Strait region highlight
    _add_strait_overlay(m)

    # Add layer control
    folium.LayerControl(collapsed=False).add_to(m)

    # Add fullscreen option
    plugins.Fullscreen().add_to(m)

    # Add coordinate display on click
    m.add_child(folium.LatLngPopup())

    # Add title
    title_html = f'''
    <div style="position: fixed;
                top: 10px; left: 50px;
                z-index: 9999;
                background-color: white;
                padding: 10px 20px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                font-family: Arial, sans-serif;">
        <h4 style="margin: 0; color: #1f2937;">{scenario.name}</h4>
        <p style="margin: 5px 0 0 0; font-size: 12px; color: #6b7280;">
            Blue: {len(scenario.blue_force.units)} units |
            Red: {len(scenario.red_force.units)} units
        </p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))

    return m


def _add_unit_marker(
    layer: folium.FeatureGroup,
    unit,
    force: str,
    show_ranges: bool,
    ranges_layer: folium.FeatureGroup
):
    """Add a unit marker to the map layer."""
    icon_config = UNIT_ICONS.get(unit.type, {"icon": "circle", "prefix": "fa"})
    color = FORCE_COLORS[force]

    # Create popup content
    popup_html = f"""
    <div style="font-family: Arial, sans-serif; min-width: 200px;">
        <h4 style="margin: 0 0 10px 0; color: {color};">{unit.name}</h4>
        <table style="font-size: 12px;">
            <tr><td><b>Type:</b></td><td>{unit.type.capitalize()}</td></tr>
            <tr><td><b>Status:</b></td><td>{unit.status.capitalize()}</td></tr>
            <tr><td><b>Grid:</b></td><td>{unit.position.grid_ref}</td></tr>
            <tr><td><b>Position:</b></td><td>{unit.position.lat:.4f}, {unit.position.lon:.4f}</td></tr>
            <tr><td><b>Range:</b></td><td>{unit.range_km} km</td></tr>
            <tr><td><b>Speed:</b></td><td>{unit.speed_kmh} km/h</td></tr>
        </table>
        <p style="font-size: 11px; color: #666; margin-top: 10px;">
            <b>Capabilities:</b> {', '.join(unit.capabilities) if unit.capabilities else 'N/A'}
        </p>
    </div>
    """

    # Create marker
    marker = folium.Marker(
        location=[unit.position.lat, unit.position.lon],
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=f"{unit.name} ({unit.type})",
        icon=folium.Icon(
            color="blue" if force == "blue" else "red",
            icon=icon_config["icon"],
            prefix=icon_config["prefix"]
        )
    )
    marker.add_to(layer)

    # Add range circle if enabled
    if show_ranges and unit.range_km > 0:
        circle = folium.Circle(
            location=[unit.position.lat, unit.position.lon],
            radius=unit.range_km * 1000,  # Convert to meters
            color=color,
            fill=True,
            fillOpacity=0.1,
            weight=1,
            tooltip=f"{unit.name} range: {unit.range_km} km"
        )
        circle.add_to(ranges_layer)


def _add_objective_marker(layer: folium.FeatureGroup, objective):
    """Add an objective marker to the map layer."""
    # Owner-based styling
    owner_colors = {
        "blue": "#2563eb",
        "red": "#dc2626",
        "contested": "#f59e0b",
        "neutral": "#6b7280"
    }
    color = owner_colors.get(objective.owner, OBJECTIVE_COLOR)

    popup_html = f"""
    <div style="font-family: Arial, sans-serif; min-width: 180px;">
        <h4 style="margin: 0 0 10px 0; color: {color};">
            ⭐ {objective.name}
        </h4>
        <p style="font-size: 12px; margin: 5px 0;">{objective.description}</p>
        <table style="font-size: 12px;">
            <tr><td><b>Owner:</b></td><td>{objective.owner.capitalize()}</td></tr>
            <tr><td><b>Value:</b></td><td>{'⭐' * objective.value}</td></tr>
            <tr><td><b>Grid:</b></td><td>{objective.position.grid_ref}</td></tr>
        </table>
    </div>
    """

    marker = folium.Marker(
        location=[objective.position.lat, objective.position.lon],
        popup=folium.Popup(popup_html, max_width=250),
        tooltip=f"Objective: {objective.name}",
        icon=folium.Icon(
            color="orange",
            icon="star",
            prefix="fa"
        )
    )
    marker.add_to(layer)


def _add_strait_overlay(m: folium.Map):
    """Add Taiwan Strait region overlay."""
    # Approximate Taiwan Strait boundaries
    strait_coords = [
        [26.0, 118.0],
        [26.0, 121.0],
        [22.5, 121.0],
        [22.5, 118.0],
        [26.0, 118.0]
    ]

    folium.PolyLine(
        locations=strait_coords,
        color="#3b82f6",
        weight=2,
        opacity=0.5,
        dash_array="10",
        tooltip="Taiwan Strait Region"
    ).add_to(m)


def create_movement_map(
    scenario,
    movements: list[dict],
    config: Optional[MapConfig] = None
) -> folium.Map:
    """
    Create a map showing unit movements.

    Args:
        scenario: The base scenario
        movements: List of movement dicts with 'unit_id', 'from', 'to' positions
        config: Map configuration

    Returns:
        Folium Map with movement arrows
    """
    m = create_scenario_map(scenario, config)

    movements_layer = folium.FeatureGroup(name="Movements")

    for move in movements:
        # Draw arrow from old to new position
        folium.PolyLine(
            locations=[
                [move["from"]["lat"], move["from"]["lon"]],
                [move["to"]["lat"], move["to"]["lon"]]
            ],
            color="#10b981",  # Green
            weight=3,
            opacity=0.8,
            tooltip=f"Movement: {move.get('unit_name', 'Unknown')}"
        ).add_to(movements_layer)

        # Add arrow head marker at destination
        folium.RegularPolygonMarker(
            location=[move["to"]["lat"], move["to"]["lon"]],
            number_of_sides=3,
            radius=8,
            rotation=0,
            color="#10b981",
            fill=True,
            fill_color="#10b981"
        ).add_to(movements_layer)

    movements_layer.add_to(m)

    return m


def save_map(m: folium.Map, filepath: Path) -> Path:
    """
    Save the map to an HTML file.

    Args:
        m: Folium Map object
        filepath: Output path (should end in .html)

    Returns:
        Path to saved file
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    m.save(str(filepath))
    return filepath


def generate_scenario_report(scenario, output_dir: Path) -> dict:
    """
    Generate a complete map report for a scenario.

    Creates multiple map views:
    - Overview map
    - Blue forces focused
    - Red forces focused
    - With ranges shown

    Args:
        scenario: Scenario object
        output_dir: Directory to save maps

    Returns:
        Dict with paths to generated files
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    files = {}

    # Overview map
    overview = create_scenario_map(scenario, show_ranges=False)
    files["overview"] = save_map(overview, output_dir / "overview.html")

    # Map with ranges
    ranges_map = create_scenario_map(scenario, show_ranges=True)
    files["ranges"] = save_map(ranges_map, output_dir / "ranges.html")

    return files


# CLI integration
def visualize_scenario(scenario_name: str, output_path: Optional[str] = None):
    """
    Visualize a scenario from the command line.

    Args:
        scenario_name: Name of the scenario to visualize
        output_path: Optional output path for HTML file
    """
    if scenario_name == "taiwan_strait":
        from ..scenarios.taiwan_strait import create_demo_scenario
        scenario = create_demo_scenario()
    else:
        raise ValueError(f"Unknown scenario: {scenario_name}")

    m = create_scenario_map(scenario, show_ranges=True)

    if output_path:
        save_map(m, Path(output_path))
        print(f"Map saved to: {output_path}")
    else:
        # Save to temp and open
        import tempfile
        import webbrowser
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            m.save(f.name)
            webbrowser.open(f"file://{f.name}")
