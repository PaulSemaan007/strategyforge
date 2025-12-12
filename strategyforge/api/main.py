"""
FastAPI backend for StrategyForge.

Provides REST API endpoints for the Next.js frontend.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import asyncio
import json
import uuid
from datetime import datetime

app = FastAPI(
    title="StrategyForge API",
    description="Multi-Agent Wargaming Evaluation System API",
    version="1.0.0"
)

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# MODELS
# ============================================================================

class ScenarioInfo(BaseModel):
    name: str
    region: str
    description: str
    blue_units: int
    red_units: int
    objectives: int


class EvaluationRequest(BaseModel):
    benchmark: str = "quick"
    model: str = "llama3.1:8b"


class SimulationRequest(BaseModel):
    scenario: str = "taiwan_strait"
    turns: int = 3
    model: str = "llama3.1:8b"


class BenchmarkInfo(BaseModel):
    name: str
    description: str
    num_cases: int


# ============================================================================
# IN-MEMORY STORAGE (for demo purposes)
# ============================================================================

simulation_results = {}
evaluation_results = {}
simulation_jobs = {}  # Stores running simulation state and messages


# ============================================================================
# ROUTES
# ============================================================================

@app.get("/")
async def root():
    """API health check."""
    return {
        "name": "StrategyForge API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "scenarios": "/api/scenarios",
            "benchmarks": "/api/benchmarks",
            "evaluate": "/api/evaluate",
            "map_data": "/api/map/{scenario}"
        }
    }


@app.get("/api/scenarios")
async def list_scenarios():
    """List all available scenarios."""
    try:
        from ..scenarios.taiwan_strait import create_demo_scenario

        scenario = create_demo_scenario()

        return {
            "scenarios": [
                {
                    "id": "taiwan_strait",
                    "name": scenario.name,
                    "region": "Indo-Pacific",
                    "description": "Taiwan Strait conflict scenario with naval and air operations",
                    "blue_units": len(scenario.blue_force.units),
                    "red_units": len(scenario.red_force.units),
                    "objectives": len(scenario.objectives),
                    "available": True
                },
                {
                    "id": "eastern_europe",
                    "name": "Eastern European Front",
                    "region": "Europe",
                    "description": "European theater scenario (coming soon)",
                    "blue_units": 0,
                    "red_units": 0,
                    "objectives": 0,
                    "available": False
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/scenarios/{scenario_id}")
async def get_scenario(scenario_id: str):
    """Get detailed scenario information."""
    if scenario_id != "taiwan_strait":
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found")

    try:
        from ..scenarios.taiwan_strait import create_demo_scenario

        scenario = create_demo_scenario()

        return {
            "id": "taiwan_strait",
            "name": scenario.name,
            "description": scenario.description,
            "blue_force": {
                "name": scenario.blue_force.name,
                "units": [
                    {
                        "id": u.id,
                        "name": u.name,
                        "type": u.type,
                        "position": {"lat": u.position.lat, "lon": u.position.lon},
                        "capabilities": u.capabilities,
                        "strength": 100 if u.status == "ready" else 50
                    }
                    for u in scenario.blue_force.units
                ]
            },
            "red_force": {
                "name": scenario.red_force.name,
                "units": [
                    {
                        "id": u.id,
                        "name": u.name,
                        "type": u.type,
                        "position": {"lat": u.position.lat, "lon": u.position.lon},
                        "capabilities": u.capabilities,
                        "strength": 100 if u.status == "ready" else 50
                    }
                    for u in scenario.red_force.units
                ]
            },
            "objectives": [
                {
                    "id": obj.id,
                    "name": obj.name,
                    "description": obj.description,
                    "position": {"lat": obj.position.lat, "lon": obj.position.lon},
                    "value": obj.value,
                    "owner": obj.owner
                }
                for obj in scenario.objectives
            ],
            "terrain_data": scenario.terrain_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/map/{scenario_id}")
async def get_map_data(scenario_id: str):
    """Get map data for visualization."""
    if scenario_id != "taiwan_strait":
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found")

    try:
        from ..scenarios.taiwan_strait import create_demo_scenario

        scenario = create_demo_scenario()

        # Generate GeoJSON-like structure for the frontend
        features = []

        # Blue units
        for unit in scenario.blue_force.units:
            features.append({
                "type": "Feature",
                "properties": {
                    "id": unit.id,
                    "name": unit.name,
                    "type": unit.type,
                    "force": "blue",
                    "strength": 100 if unit.status == "ready" else 50,
                    "capabilities": unit.capabilities
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [unit.position.lon, unit.position.lat]  # [lon, lat]
                }
            })

        # Red units
        for unit in scenario.red_force.units:
            features.append({
                "type": "Feature",
                "properties": {
                    "id": unit.id,
                    "name": unit.name,
                    "type": unit.type,
                    "force": "red",
                    "strength": 100 if unit.status == "ready" else 50,
                    "capabilities": unit.capabilities
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [unit.position.lon, unit.position.lat]
                }
            })

        # Objectives
        for obj in scenario.objectives:
            features.append({
                "type": "Feature",
                "properties": {
                    "id": obj.id,
                    "name": obj.name,
                    "type": "objective",
                    "value": obj.value,
                    "owner": obj.owner
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [obj.position.lon, obj.position.lat]
                }
            })

        return {
            "type": "FeatureCollection",
            "features": features,
            "bounds": {
                "center": [24.5, 120.5],
                "zoom": 7
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/benchmarks")
async def list_benchmarks():
    """List all available benchmarks."""
    try:
        from ..evaluation.benchmarks import list_benchmarks as get_benchmarks

        return {
            "benchmarks": get_benchmarks()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/benchmarks/{benchmark_name}")
async def get_benchmark(benchmark_name: str):
    """Get detailed benchmark information."""
    try:
        from ..evaluation.benchmarks import get_benchmark as fetch_benchmark

        benchmark = fetch_benchmark(benchmark_name)

        return {
            "name": benchmark.name,
            "description": benchmark.description,
            "cases": [
                {
                    "id": case.id,
                    "name": case.name,
                    "category": case.category.value,
                    "difficulty": case.difficulty,
                    "prompt_preview": case.prompt[:200] + "..." if len(case.prompt) > 200 else case.prompt
                }
                for case in benchmark.cases
            ]
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/evaluate")
async def run_evaluation(request: EvaluationRequest, background_tasks: BackgroundTasks):
    """Run evaluation benchmark (async)."""
    import uuid

    job_id = str(uuid.uuid4())[:8]
    evaluation_results[job_id] = {"status": "pending", "progress": 0}

    # Run in background
    background_tasks.add_task(
        _run_evaluation_task,
        job_id,
        request.benchmark,
        request.model
    )

    return {
        "job_id": job_id,
        "status": "started",
        "message": f"Evaluation started with benchmark '{request.benchmark}'"
    }


async def _run_evaluation_task(job_id: str, benchmark: str, model: str):
    """Background task to run evaluation."""
    try:
        evaluation_results[job_id]["status"] = "running"

        from ..evaluation.runner import EvaluationRunner

        runner = EvaluationRunner(model_name=model, verbose=False)
        report = runner.run_benchmark(benchmark)

        evaluation_results[job_id] = {
            "status": "completed",
            "result": report.to_dict()
        }
    except Exception as e:
        evaluation_results[job_id] = {
            "status": "failed",
            "error": str(e)
        }


@app.get("/api/evaluate/{job_id}")
async def get_evaluation_status(job_id: str):
    """Get evaluation job status."""
    if job_id not in evaluation_results:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")

    return evaluation_results[job_id]


@app.get("/api/metrics")
async def get_metric_definitions():
    """Get evaluation metric definitions."""
    return {
        "categories": [
            {
                "id": "geospatial",
                "name": "Geospatial Reasoning",
                "description": "Ability to reason about distances, terrain, and geography",
                "metrics": [
                    {"name": "Distance Accuracy", "description": "Correct distance calculations"},
                    {"name": "Grid Reference Usage", "description": "Use of proper military grid references"},
                    {"name": "Terrain Awareness", "description": "Understanding of terrain effects"}
                ]
            },
            {
                "id": "strategic",
                "name": "Strategic Coherence",
                "description": "Quality of strategic decision-making",
                "metrics": [
                    {"name": "Objective Alignment", "description": "Decisions support stated objectives"},
                    {"name": "Reasoning Structure", "description": "Logical flow of reasoning"},
                    {"name": "Decision Consistency", "description": "Consistency across turns"}
                ]
            },
            {
                "id": "adversarial",
                "name": "Adversarial Reasoning",
                "description": "Ability to model and counter opponent actions",
                "metrics": [
                    {"name": "Opponent Modeling", "description": "Anticipation of enemy moves"},
                    {"name": "Multi-Step Planning", "description": "Planning multiple moves ahead"}
                ]
            }
        ]
    }


# ============================================================================
# SIMULATION ENDPOINTS
# ============================================================================

@app.post("/api/simulation/start")
async def start_simulation(request: SimulationRequest, background_tasks: BackgroundTasks):
    """Start a new wargaming simulation with LangGraph agents."""
    job_id = str(uuid.uuid4())[:8]

    # Initialize job state
    simulation_jobs[job_id] = {
        "status": "starting",
        "messages": [],
        "new_messages": [],  # Messages not yet streamed to client
        "turn": 0,
        "max_turns": request.turns,
        "scenario": request.scenario,
        "model": request.model,
        "created_at": datetime.now().isoformat()
    }

    # Run simulation in background
    background_tasks.add_task(
        _run_simulation_task,
        job_id,
        request.scenario,
        request.turns,
        request.model
    )

    return {
        "job_id": job_id,
        "status": "started",
        "message": f"Simulation started for scenario '{request.scenario}' with {request.turns} turns"
    }


@app.get("/api/simulation/{job_id}/stream")
async def stream_simulation(job_id: str):
    """Stream simulation messages via Server-Sent Events."""
    if job_id not in simulation_jobs:
        raise HTTPException(status_code=404, detail=f"Simulation job '{job_id}' not found")

    async def event_generator():
        """Generate SSE events for simulation updates."""
        last_message_count = 0

        while True:
            job = simulation_jobs.get(job_id)
            if not job:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Job not found'})}\n\n"
                break

            # Send any new messages
            current_count = len(job["messages"])
            if current_count > last_message_count:
                for msg in job["messages"][last_message_count:]:
                    yield f"data: {json.dumps({'type': 'message', **msg})}\n\n"
                last_message_count = current_count

            # Send status updates
            if job["status"] == "completed":
                yield f"data: {json.dumps({'type': 'status', 'status': 'completed', 'turn': job['turn']})}\n\n"
                break
            elif job["status"] == "failed":
                yield f"data: {json.dumps({'type': 'error', 'message': job.get('error', 'Unknown error')})}\n\n"
                break

            await asyncio.sleep(0.5)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )


@app.get("/api/simulation/{job_id}")
async def get_simulation_status(job_id: str):
    """Get the current status of a simulation job."""
    if job_id not in simulation_jobs:
        raise HTTPException(status_code=404, detail=f"Simulation job '{job_id}' not found")

    job = simulation_jobs[job_id]
    return {
        "job_id": job_id,
        "status": job["status"],
        "turn": job["turn"],
        "max_turns": job["max_turns"],
        "message_count": len(job["messages"]),
        "messages": job["messages"]
    }


async def _run_simulation_task(job_id: str, scenario_id: str, max_turns: int, model: str):
    """Background task to run the LangGraph simulation."""
    try:
        simulation_jobs[job_id]["status"] = "running"

        # Import the graph and scenario
        from ..agents.graph import create_wargame_graph
        from ..agents.state import create_state_from_scenario
        from ..scenarios.taiwan_strait import create_demo_scenario

        # Create scenario and initial state
        scenario = create_demo_scenario()
        initial_state = create_state_from_scenario(scenario, max_turns)

        # Create and run the graph
        graph = create_wargame_graph()

        # Track which messages we've seen
        seen_message_ids = set()

        # Run with streaming
        async for state_update in graph.astream(initial_state):
            # Process each node's output
            for node_name, node_state in state_update.items():
                if "messages" in node_state:
                    for msg in node_state["messages"]:
                        # Create unique ID for message
                        msg_id = f"{node_name}_{len(simulation_jobs[job_id]['messages'])}"

                        if msg_id not in seen_message_ids:
                            seen_message_ids.add(msg_id)

                            # Get agent name from message
                            agent_name = getattr(msg, 'name', node_name)

                            # Format message for frontend
                            formatted_msg = {
                                "agent": agent_name,
                                "content": msg.content,
                                "turn": node_state.get("turn_number", simulation_jobs[job_id]["turn"]),
                                "timestamp": datetime.now().strftime("%H:%M:%S")
                            }

                            # Add to messages list
                            simulation_jobs[job_id]["messages"].append(formatted_msg)

                # Update turn number if present
                if "turn_number" in node_state:
                    simulation_jobs[job_id]["turn"] = node_state["turn_number"]

        simulation_jobs[job_id]["status"] = "completed"

    except Exception as e:
        import traceback
        simulation_jobs[job_id]["status"] = "failed"
        simulation_jobs[job_id]["error"] = f"{str(e)}\n{traceback.format_exc()}"


# Demo evaluation result for testing
@app.get("/api/demo/evaluation")
async def get_demo_evaluation():
    """Get a demo evaluation result for frontend testing."""
    return {
        "model_name": "llama3.1:8b",
        "scenario_name": "quick",
        "total_turns": 3,
        "overall_score": 0.542,
        "overall_percentage": 54.2,
        "category_scores": {
            "geospatial": 0.511,
            "strategic": 0.656,
            "adversarial": 0.417
        },
        "metrics": [
            {"name": "Distance Accuracy", "category": "geospatial", "score": 0.5, "grade": "F", "details": "1 distance claims found"},
            {"name": "Grid Reference Usage", "category": "geospatial", "score": 0.3, "grade": "F", "details": "No grid references used"},
            {"name": "Terrain Awareness", "category": "geospatial", "score": 0.73, "grade": "C", "details": "Referenced 4 terrain concepts"},
            {"name": "Objective Alignment", "category": "strategic", "score": 0.5, "grade": "F", "details": "No objectives specified"},
            {"name": "Reasoning Structure", "category": "strategic", "score": 0.75, "grade": "C", "details": "Included 3/4 reasoning elements"},
            {"name": "Decision Consistency", "category": "strategic", "score": 0.72, "grade": "C", "details": "First response"},
            {"name": "Opponent Modeling", "category": "adversarial", "score": 0.5, "grade": "F", "details": "Referenced opponent 2 times"},
            {"name": "Multi-Step Planning", "category": "adversarial", "score": 0.33, "grade": "F", "details": "Found 1 multi-step indicators"}
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
