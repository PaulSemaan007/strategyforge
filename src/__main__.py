"""
StrategyForge CLI - Multi-Agent Wargaming Evaluation System

Usage:
    python -m strategyforge run --scenario taiwan_strait
    python -m strategyforge evaluate --benchmark full
    python -m strategyforge scenarios --list
"""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.markdown import Markdown

app = typer.Typer(
    name="strategyforge",
    help="Multi-Agent Wargaming Evaluation System",
    add_completion=False
)

console = Console()


@app.command()
def run(
    scenario: str = typer.Option(
        "taiwan_strait",
        "--scenario", "-s",
        help="Scenario to run (taiwan_strait, eastern_europe, custom)"
    ),
    turns: int = typer.Option(
        5,
        "--turns", "-t",
        help="Maximum number of turns to simulate"
    ),
    model: str = typer.Option(
        "llama3.1:8b",
        "--model", "-m",
        help="Ollama model to use"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Show detailed agent reasoning"
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Save simulation results to file"
    )
):
    """
    Run a wargaming simulation.

    Example:
        python -m strategyforge run --scenario taiwan_strait --turns 5
    """
    console.print(Panel.fit(
        "[bold blue]StrategyForge[/bold blue] - Multi-Agent Wargaming Simulation",
        subtitle="Powered by LangGraph + Ollama"
    ))

    # Load scenario
    console.print(f"\n[yellow]Loading scenario:[/yellow] {scenario}")

    try:
        if scenario == "taiwan_strait":
            from .scenarios.taiwan_strait import create_demo_scenario
            game_scenario = create_demo_scenario()
        else:
            console.print(f"[red]Unknown scenario: {scenario}[/red]")
            console.print("Available scenarios: taiwan_strait")
            raise typer.Exit(1)

        console.print(f"[green]Scenario loaded:[/green] {game_scenario.name}")
        console.print(game_scenario.summary())

        # Run simulation
        console.print(f"\n[yellow]Starting simulation ({turns} turns max)...[/yellow]\n")

        asyncio.run(_run_simulation(game_scenario, turns, model, verbose, output))

    except ImportError as e:
        console.print(f"[red]Missing dependency:[/red] {e}")
        console.print("Run: pip install -r requirements.txt")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


async def _run_simulation(scenario, max_turns: int, model: str, verbose: bool, output: Optional[Path]):
    """Run the async simulation loop."""
    from .agents.graph import create_wargame_graph
    from .agents.state import create_initial_state

    # Create initial state
    initial_state = create_initial_state(
        scenario_name=scenario.name,
        blue_units=[u.to_dict() for u in scenario.blue_force.units],
        red_units=[u.to_dict() for u in scenario.red_force.units],
        objectives={obj.id: obj.to_dict() for obj in scenario.objectives},
        terrain_data=scenario.terrain_data
    )

    # Create and run graph
    graph = create_wargame_graph()

    console.print("[bold]Simulation Running...[/bold]\n")

    current_turn = 0
    results = []

    try:
        async for state_update in graph.astream(initial_state):
            # Get the node name and state
            for node_name, node_state in state_update.items():
                if "messages" in node_state and node_state["messages"]:
                    last_message = node_state["messages"][-1]

                    # Display agent output
                    agent_name = getattr(last_message, "name", node_name)
                    agent_colors = {
                        "blue_commander": "blue",
                        "red_commander": "red",
                        "analyst": "green"
                    }
                    color = agent_colors.get(agent_name, "white")

                    console.print(Panel(
                        Markdown(last_message.content[:2000] + "..." if len(last_message.content) > 2000 else last_message.content),
                        title=f"[bold {color}]{agent_name.upper()}[/bold {color}]",
                        border_style=color
                    ))

                    if verbose:
                        console.print(f"[dim]Full reasoning: {len(last_message.content)} chars[/dim]")

                    results.append({
                        "agent": agent_name,
                        "content": last_message.content
                    })

                # Track turn progress
                if "turn_number" in node_state:
                    new_turn = node_state["turn_number"]
                    if new_turn != current_turn:
                        current_turn = new_turn
                        if current_turn > max_turns:
                            console.print(f"\n[yellow]Maximum turns ({max_turns}) reached.[/yellow]")
                            break
                        console.print(f"\n[bold cyan]═══ Turn {current_turn} ═══[/bold cyan]\n")

    except KeyboardInterrupt:
        console.print("\n[yellow]Simulation interrupted by user.[/yellow]")

    # Summary
    console.print(Panel.fit(
        f"[bold]Simulation Complete[/bold]\n"
        f"Turns: {current_turn}\n"
        f"Total agent responses: {len(results)}",
        title="Summary",
        border_style="green"
    ))

    # Save results if output specified
    if output:
        import json
        with open(output, "w") as f:
            json.dump({
                "scenario": scenario.name,
                "turns": current_turn,
                "results": results
            }, f, indent=2)
        console.print(f"[green]Results saved to:[/green] {output}")


@app.command()
def evaluate(
    benchmark: str = typer.Option(
        "quick",
        "--benchmark", "-b",
        help="Benchmark suite to run (quick, full, geospatial, strategic)"
    ),
    model: str = typer.Option(
        "llama3.1:8b",
        "--model", "-m",
        help="Ollama model to evaluate"
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Save evaluation results to file"
    )
):
    """
    Run evaluation benchmarks on LLM wargaming capabilities.

    Example:
        python -m strategyforge evaluate --benchmark geospatial
    """
    console.print(Panel.fit(
        "[bold blue]StrategyForge[/bold blue] - LLM Evaluation Framework",
        subtitle="Measuring wargaming capabilities"
    ))

    console.print(f"\n[yellow]Running benchmark:[/yellow] {benchmark}")
    console.print(f"[yellow]Model:[/yellow] {model}")

    # TODO: Implement evaluation framework (Phase 3)
    console.print("\n[dim]Evaluation framework coming in Phase 3...[/dim]")

    table = Table(title="Evaluation Metrics (Preview)")
    table.add_column("Metric", style="cyan")
    table.add_column("Score", justify="right")
    table.add_column("Status", justify="center")

    metrics = [
        ("Geospatial Accuracy", "—", "[dim]Pending[/dim]"),
        ("Strategic Coherence", "—", "[dim]Pending[/dim]"),
        ("Resource Awareness", "—", "[dim]Pending[/dim]"),
        ("Adversarial Reasoning", "—", "[dim]Pending[/dim]"),
        ("Risk Calibration", "—", "[dim]Pending[/dim]"),
    ]

    for metric, score, status in metrics:
        table.add_row(metric, score, status)

    console.print(table)


@app.command()
def scenarios(
    list_all: bool = typer.Option(
        False,
        "--list", "-l",
        help="List all available scenarios"
    ),
    info: Optional[str] = typer.Option(
        None,
        "--info", "-i",
        help="Show detailed info about a scenario"
    )
):
    """
    Manage wargaming scenarios.

    Example:
        python -m strategyforge scenarios --list
    """
    if list_all:
        console.print(Panel.fit(
            "[bold blue]Available Scenarios[/bold blue]"
        ))

        table = Table()
        table.add_column("Name", style="cyan")
        table.add_column("Region")
        table.add_column("Blue Units", justify="right")
        table.add_column("Red Units", justify="right")

        # List available scenarios
        scenarios_data = [
            ("taiwan_strait", "Indo-Pacific", "8", "9"),
            ("eastern_europe", "Europe", "—", "—"),
        ]

        for name, region, blue, red in scenarios_data:
            status = "" if blue != "—" else " [dim](coming soon)[/dim]"
            table.add_row(name + status, region, blue, red)

        console.print(table)

    if info:
        console.print(f"\n[yellow]Scenario Info:[/yellow] {info}")

        if info == "taiwan_strait":
            from .scenarios.taiwan_strait import create_demo_scenario
            scenario = create_demo_scenario()
            console.print(scenario.summary())
        else:
            console.print(f"[red]Unknown scenario: {info}[/red]")


@app.command()
def api(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind to"),
    reload: bool = typer.Option(False, "--reload", "-r", help="Enable auto-reload")
):
    """
    Start the FastAPI backend server.

    Example:
        python -m strategyforge api --port 8000
    """
    console.print(Panel.fit(
        "[bold blue]StrategyForge API Server[/bold blue]",
        subtitle=f"Starting on http://{host}:{port}"
    ))

    try:
        import uvicorn
        uvicorn.run(
            "strategyforge.src.api.main:app",
            host=host,
            port=port,
            reload=reload
        )
    except ImportError:
        console.print("[red]uvicorn not installed.[/red] Run: pip install uvicorn")
        raise typer.Exit(1)


@app.callback()
def main():
    """
    StrategyForge - Multi-Agent Wargaming Evaluation System

    A demonstration of LLM agent architecture, geospatial reasoning,
    and evaluation tooling for military decision-making scenarios.
    """
    pass


if __name__ == "__main__":
    app()
