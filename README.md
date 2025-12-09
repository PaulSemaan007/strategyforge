# StrategyForge

**Multi-Agent Wargaming Evaluation System**

A LangGraph-powered simulation platform where LLM agents act as military commanders, making strategic decisions with geospatial reasoning. Built to demonstrate AI capabilities in military decision-making and evaluate LLM effectiveness in wargaming scenarios.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green.svg)
![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## Demo

<p align="center">
  <img src="docs/dashboard.png" alt="Dashboard" width="45%">
  <img src="docs/map.png" alt="Tactical Map" width="45%">
</p>

**Live Demo**: [strategyforge.vercel.app](https://strategyforge.vercel.app) *(coming soon)*

---

## Overview

StrategyForge is a research platform exploring how Large Language Models can support military wargaming and strategic planning. It features:

- **Multi-Agent Architecture**: Blue Force, Red Force, and Analyst agents in a turn-based simulation
- **Geospatial Reasoning**: Agents calculate distances, analyze terrain, and reason about geography
- **Evaluation Framework**: Comprehensive metrics to measure LLM effectiveness in strategic decision-making
- **Interactive Web UI**: Real-time visualization with tactical maps and evaluation dashboards
- **Realistic Scenarios**: Indo-Pacific theater configurations with 17+ military units

```
┌─────────────────────────────────────────────────────────────────┐
│                      STRATEGYFORGE SYSTEM                        │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ Interactive  │  │ Agent Chat   │  │ Evaluation Dashboard │   │
│  │ Map (Leaflet)│  │ Logs Panel   │  │ (Metrics & Charts)   │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
│                              │                                   │
│                    ┌─────────▼─────────┐                        │
│                    │   FastAPI Backend │                        │
│                    └─────────┬─────────┘                        │
│                              │                                   │
│   ┌─────────────┐    ┌──────▼──────┐    ┌─────────────┐        │
│   │ BLUE FORCE  │    │ LANGGRAPH   │    │ RED FORCE   │        │
│   │ Commander   │◄──►│ Agent Graph │◄──►│ Commander   │        │
│   └─────────────┘    └──────┬──────┘    └─────────────┘        │
│                             │                                    │
│                    ┌────────▼────────┐                          │
│                    │ ANALYST AGENT   │                          │
│                    │ + Evaluation    │                          │
│                    └─────────────────┘                          │
│                             │                                    │
│                    ┌────────▼────────┐                          │
│                    │ Ollama (Llama)  │                          │
│                    └─────────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for web UI)
- [Ollama](https://ollama.ai/) with `llama3.1:8b` model

### Installation

```bash
# Clone the repository
git clone https://github.com/PaulSemaan007/strategyforge.git
cd strategyforge

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Pull the Ollama model
ollama pull llama3.1:8b
```

### Run a Simulation (CLI)

```bash
# Run the Taiwan Strait scenario
python -m strategyforge run --scenario taiwan_strait --turns 5

# With verbose output
python -m strategyforge run -s taiwan_strait -t 3 --verbose

# Save results to file
python -m strategyforge run -s taiwan_strait -o results.json
```

### Run Evaluation Benchmarks

```bash
# Quick benchmark (3 test cases)
python -m strategyforge evaluate --benchmark quick

# Full evaluation suite (10 test cases)
python -m strategyforge evaluate --benchmark full

# Category-specific benchmarks
python -m strategyforge evaluate --benchmark geospatial
python -m strategyforge evaluate --benchmark strategic
python -m strategyforge evaluate --benchmark adversarial
```

### Generate Tactical Map

```bash
# Generate interactive HTML map
python -m strategyforge map --scenario taiwan_strait --output map.html
```

### Run the Web UI

```bash
# Start the FastAPI backend
python -m strategyforge api --port 8000

# In a new terminal, start the Next.js frontend
cd web
npm install
npm run dev

# Open http://localhost:3000
```

---

## Evaluation Framework

The evaluation system measures LLM performance across three critical domains:

### Metrics Categories

| Category | Metrics | What It Measures |
|----------|---------|------------------|
| **Geospatial** | Distance Accuracy, Grid Reference Usage, Terrain Awareness | Can the LLM correctly reason about geography? |
| **Strategic** | Objective Alignment, Reasoning Structure, Decision Consistency | Are decisions logically sound? |
| **Adversarial** | Opponent Modeling, Multi-Step Planning | Can the LLM anticipate enemy actions? |

### Benchmark Results (Llama 3.1 8B)

```
=== Evaluation Report ===
Model: llama3.1:8b
Benchmark: quick

Overall Score: 54.2%

Category Breakdown:
  Geospatial: 51.1%
  Strategic: 65.6%
  Adversarial: 41.7%

Individual Metrics:
  [F] Distance Accuracy: 50.0%
  [F] Grid Reference Usage: 30.0%
  [C] Terrain Awareness: 73.3%
  [F] Objective Alignment: 50.0%
  [C] Reasoning Structure: 75.0%
  [C] Decision Consistency: 72.0%
  [F] Opponent Modeling: 50.0%
  [F] Multi-Step Planning: 33.3%
```

### Benchmark Test Cases

The system includes 10 benchmark test cases:

**Geospatial (4 cases)**
- Taiwan Strait Width calculation
- Fighter Intercept Range planning
- Terrain Advantage Assessment
- Multi-Asset Coordination timing

**Strategic (3 cases)**
- Objective Prioritization
- Risk Assessment
- Resource Allocation

**Adversarial (3 cases)**
- Opponent Prediction
- Counter-Move Planning
- Deception Recognition

---

## Project Structure

```
strategyforge/
├── strategyforge/
│   ├── agents/           # LangGraph agent system
│   │   ├── graph.py      # Main agent graph
│   │   ├── prompts.py    # Agent prompt engineering
│   │   └── state.py      # Game state management
│   ├── scenarios/        # Wargame scenarios
│   │   ├── base.py       # Scenario base classes
│   │   └── taiwan_strait.py
│   ├── evaluation/       # LLM evaluation framework
│   │   ├── metrics.py    # Evaluation metrics
│   │   ├── benchmarks.py # Test suites
│   │   └── runner.py     # Benchmark runner
│   ├── geo/              # Geospatial utilities
│   │   ├── distance.py   # Haversine calculations
│   │   ├── terrain.py    # Terrain analysis
│   │   └── visualization.py  # Folium maps
│   └── api/              # FastAPI backend
│       └── main.py       # REST API endpoints
├── web/                  # Next.js frontend
│   ├── app/              # App router pages
│   │   ├── page.tsx      # Dashboard
│   │   ├── map/          # Tactical map
│   │   ├── evaluation/   # Eval results
│   │   └── simulation/   # Simulation viewer
│   └── components/       # React components
├── tests/                # Test suite
└── requirements.txt
```

---

## Key Components

### Agent System

The simulation uses three specialized agents orchestrated by LangGraph:

| Agent | Role | Perspective |
|-------|------|-------------|
| **Blue Commander** | Commands friendly forces | Defensive, mission-focused |
| **Red Commander** | Commands adversary forces | Offensive, exploitative |
| **Analyst** | Neutral evaluator | Objective, scoring-focused |

### Turn Flow

```
Turn N:
  1. Blue Commander analyzes situation → recommends action
  2. Red Commander observes Blue's move → plans counter
  3. Analyst evaluates both decisions → scores performance
  4. State updates → Turn N+1
```

### Prompt Engineering

Demonstrates structured prompting for military decision-making:

```python
BLUE_COMMANDER = """You are the BLUE FORCE COMMANDER...

## Decision Framework
When making decisions, always consider:
1. **Geospatial Factors**: Distances, terrain, chokepoints
2. **Force Disposition**: Current positions, readiness
3. **Intelligence**: Known and suspected enemy positions
4. **Objectives**: Primary and secondary mission goals
5. **Risk Assessment**: Potential losses vs. strategic gains

## Response Format
Structure your responses as:
### SITUATION ASSESSMENT
### RECOMMENDED ACTION
### RATIONALE
### RISKS & MITIGATIONS
"""
```

---

## Scenarios

### Taiwan Strait Crisis

Indo-Pacific scenario featuring:
- Maritime chokepoint control
- Multi-domain operations (air, naval, coastal)
- Distance calculations across 130km strait
- Asymmetric force considerations

**Blue Force (8 units)**
- 2x Fighter Squadrons (F-16)
- 2x Destroyer Groups
- 1x Submarine
- 2x Coastal Defense Batteries
- 1x Headquarters

**Red Force (9 units)**
- 1x Carrier Strike Group
- 2x Destroyer Groups
- 2x Submarines
- 1x Amphibious Group
- 1x Bomber Squadron
- 1x Missile Battery
- 1x Headquarters

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Agent Framework | LangGraph | Multi-agent orchestration |
| LLM Backend | Ollama (Llama 3.1) | Local inference |
| Geospatial | Folium, Haversine | Map visualization, distance calc |
| API | FastAPI | REST endpoints |
| Frontend | Next.js 14, Tailwind | Web UI |
| Maps | Leaflet, react-leaflet | Interactive tactical maps |
| Charts | Recharts | Evaluation visualizations |
| CLI | Typer + Rich | Terminal interface |

---

## API Endpoints

```
GET  /api/scenarios          # List available scenarios
GET  /api/scenarios/:id      # Get scenario details
GET  /api/map/:scenario      # Get map GeoJSON data
GET  /api/benchmarks         # List benchmarks
GET  /api/benchmarks/:name   # Get benchmark details
POST /api/evaluate           # Run evaluation (async)
GET  /api/evaluate/:job_id   # Get evaluation status
GET  /api/metrics            # Get metric definitions
GET  /api/demo/evaluation    # Demo evaluation data
```

---

## Deployment

### Vercel (Frontend)

```bash
cd web
vercel --prod
```

### Docker (Full Stack)

```bash
docker-compose up -d
```

---

## Development

```bash
# Run tests
pytest tests/

# Format code
black strategyforge/
ruff check strategyforge/

# Run API server with hot reload
python -m strategyforge api --reload

# Run frontend dev server
cd web && npm run dev
```

---

## Roadmap

- [x] Phase 1: Core agent system (LangGraph)
- [x] Phase 2: Geospatial integration (Folium, terrain)
- [x] Phase 3: Evaluation framework (10 benchmarks)
- [x] Phase 4: Web UI (Next.js, Leaflet)
- [ ] Phase 5: Additional scenarios (Eastern Europe)
- [ ] Phase 6: Model comparison (GPT-4, Claude)

---

## Research Context

This project explores questions relevant to AI-enabled military decision support:

- How accurately can LLMs reason about geography and distances?
- Can multi-agent systems provide adversarial analysis?
- What metrics best evaluate strategic decision quality?
- How should AI recommendations be presented for human oversight?

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Acknowledgments

Inspired by research into AI applications for military planning and wargaming, including:
- DOD Thunderforge initiative
- DARPA strategic planning programs
- Academic research on LLM reasoning capabilities

---

*Built as a demonstration of LLM agent architecture, geospatial AI, and evaluation tooling for the Anduril Thunderforge team.*
