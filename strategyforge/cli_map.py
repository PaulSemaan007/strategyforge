"""
Map visualization CLI command for StrategyForge.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

console = Console()


def map_command(
    scenario: str = typer.Option(
        "taiwan_strait",
        "--scenario", "-s",
        help="Scenario to visualize"
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Save map to HTML file"
    ),
    show_ranges: bool = typer.Option(
        False,
        "--ranges", "-r",
        help="Show unit operational ranges"
    ),
    open_browser: bool = typer.Option(
        True,
        "--open/--no-open",
        help="Open map in browser"
    )
):
    """
    Generate an interactive map of a scenario.

    Example:
        python -m strategyforge map --scenario taiwan_strait --ranges
    """
    console.print(Panel.fit(
        "[bold blue]StrategyForge[/bold blue] - Map Visualization",
        subtitle="Interactive scenario mapping"
    ))

    try:
        # Load scenario
        if scenario == "taiwan_strait":
            from .scenarios.taiwan_strait import create_demo_scenario
            game_scenario = create_demo_scenario()
        else:
            console.print(f"[red]Unknown scenario: {scenario}[/red]")
            raise typer.Exit(1)

        console.print(f"[yellow]Generating map for:[/yellow] {game_scenario.name}")

        # Create map
        from .geo.visualization import create_scenario_map, save_map
        m = create_scenario_map(game_scenario, show_ranges=show_ranges)

        # Save or display
        if output:
            save_map(m, output)
            console.print(f"[green]Map saved to:[/green] {output}")
            if open_browser:
                import webbrowser
                webbrowser.open(f"file://{output.absolute()}")
        else:
            # Save to temp and open
            import tempfile
            import webbrowser
            with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w") as f:
                m.save(f.name)
                temp_path = f.name
            console.print(f"[green]Map generated:[/green] {temp_path}")
            if open_browser:
                webbrowser.open(f"file://{temp_path}")

        console.print(f"\n[dim]Blue units: {len(game_scenario.blue_force.units)} | Red units: {len(game_scenario.red_force.units)}[/dim]")

    except ImportError as e:
        console.print(f"[red]Missing dependency:[/red] {e}")
        console.print("Run: pip install folium")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        import traceback
        traceback.print_exc()
        raise typer.Exit(1)
