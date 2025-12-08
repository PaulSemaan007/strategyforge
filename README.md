# StrategyForge

**Multi-Agent Wargaming Evaluation System**

A LangGraph-powered simulation platform where LLM agents act as military commanders, making strategic decisions with geospatial reasoning. Built to demonstrate AI capabilities in military decision-making and evaluate LLM effectiveness in wargaming scenarios.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## Overview

StrategyForge is a research platform exploring how Large Language Models can support military wargaming and strategic planning. It features:

- **Multi-Agent Architecture**: Blue Force, Red Force, and Analyst agents in a turn-based simulation
- **Geospatial Reasoning**: Agents calculate distances, analyze terrain, and reason about geography
- **Evaluation Framework**: Metrics to measure LLM effectiveness in strategic decision-making
- **Realistic Scenarios**: Indo-Pacific and European theater configurations

```
┌─────────────────────────────────────────────────────────────────┐
│                    LANGGRAPH AGENT SYSTEM                        │
│                                                                  │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│   │ BLUE FORCE  │    │ RED FORCE   │    │ ANALYST     │         │
│   │ Commander   │◄──►│ Commander   │◄──►│ Agent       │         │
│   └─────────────┘    └─────────────┘    └─────────────┘         │
│          │                  │                  │                 │
│          └──────────────────┼──────────────────┘                 │
│                             ▼                                    │
│                    ┌─────────────────┐                          │
│                    │ GEOSPATIAL      │                          │
│                    │ REASONING TOOLS │                          │
│                    └─────────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Prerequisites

- Python 3.11+
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

### Run a Simulation

```bash
# Run the Taiwan Strait scenario
python -m strategyforge run --scenario taiwan_strait --turns 5

# With verbose output
python -m strategyforge run -s taiwan_strait -t 3 --verbose

# Save results to file
python -m strategyforge run -s taiwan_strait -o results.json
```

---

## Architecture

### Agent System

The simulation uses three specialized agents:

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

### Evaluation Metrics

| Metric | Description |
|--------|-------------|
| **Geospatial Accuracy** | Correctness of distance/terrain calculations |
| **Strategic Coherence** | Logical consistency of decisions |
| **Resource Awareness** | Tracking of logistics and supplies |
| **Adversarial Reasoning** | Anticipation of opponent moves |
| **Risk Calibration** | Proportionate risk-taking |

---

## Project Structure

```
strategyforge/
├── src/
│   ├── agents/           # LangGraph agent system
│   │   ├── graph.py      # Main agent graph
│   │   ├── prompts.py    # Agent prompt engineering
│   │   └── state.py      # Game state management
│   ├── scenarios/        # Wargame scenarios
│   │   ├── base.py       # Scenario base classes
│   │   └── taiwan_strait.py
│   ├── evaluation/       # LLM evaluation framework
│   ├── geo/              # Geospatial utilities
│   └── api/              # FastAPI backend
├── frontend/             # Next.js UI (Vercel-ready)
├── data/                 # GeoJSON and scenario data
└── tests/                # Test suite
```

---

## Key Components

### Prompt Engineering (`src/agents/prompts.py`)

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

### Scenario System (`src/scenarios/`)

Realistic military scenarios with:
- Unit positions and capabilities
- Strategic objectives
- Terrain data
- Force composition

### Agent Graph (`src/agents/graph.py`)

LangGraph-based state machine:
- Turn-based execution
- State persistence
- Conditional routing
- Streaming output

---

## Scenarios

### Taiwan Strait Crisis

Indo-Pacific scenario testing:
- Maritime chokepoint control
- Multi-domain operations (air, naval, ground)
- Distance calculations across 180km strait
- Asymmetric force considerations

**Blue Force**: 8 units (air, naval, coastal defense)
**Red Force**: 9 units (carrier group, amphibious, missile)

---

## Evaluation Framework

*(Phase 3 - In Progress)*

The evaluation system measures LLM performance on:

1. **Geospatial Benchmarks**
   - Distance calculation accuracy
   - Terrain understanding
   - Position reasoning

2. **Strategic Benchmarks**
   - Decision consistency
   - Objective alignment
   - Resource management

3. **Adversarial Benchmarks**
   - Opponent modeling
   - Counter-move prediction
   - Deception detection

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Agent Framework | LangGraph |
| LLM Backend | Ollama (Llama 3.1) |
| Geospatial | GeoPandas, Folium |
| API | FastAPI |
| Frontend | Next.js (Vercel) |
| CLI | Typer + Rich |

---

## Development

```bash
# Run tests
pytest tests/

# Format code
black src/
ruff check src/

# Run API server
python -m strategyforge api --reload
```

---

## Roadmap

- [x] Phase 1: Core agent system
- [x] Phase 2: Geospatial integration
- [ ] Phase 3: Evaluation framework
- [ ] Phase 4: Web UI (Next.js)
- [ ] Phase 5: Additional scenarios

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

*Built as a demonstration of LLM agent architecture, geospatial AI, and evaluation tooling.*
