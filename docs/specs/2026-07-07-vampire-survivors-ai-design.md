# Vampire Survivors AI — Design Specification

**Date:** 2026-07-07
**Author:** Jonathan Kubicki
**Status:** Approved

## 1. Purpose

Build a Pygame Vampire Survivors clone with a locally-run LLM agent that plays the game autonomously. The project serves as a learning vehicle for understanding how LLMs handle spatial reasoning, threat assessment, risk/reward tradeoffs, and real-time decision-making when used as game-playing agents.

Inspired by [Ramp Labs' AI Plays RollerCoaster Tycoon](https://labs.ramp.com/rct), which demonstrated how Claude Code handles economic reasoning. This project explores the complementary question: **can an LLM do fast spatial reasoning?**

## 2. Milestones

| # | Milestone | Deliverable | Writeup Focus |
|---|---|---|---|
| M1 | Pygame VS Clone | Playable game: player movement, auto-attack, enemy waves, pickups, HP, death | N/A (foundation) |
| M2 | Step-Lock AI (Structured State) | LLM receives JSON game state, outputs movement via Ollama | Decision latency, survival time vs. human baseline, action distribution |
| M3 | Metrics & Analysis Framework | Automated logging, replay system, performance dashboards | Throughput, think-time histograms, decision quality scoring |
| M4 | Async Real-Time Mode | AI plays in real-time, game doesn't wait | Latency impact on survival, step-lock vs. async comparison |
| M5 | Vision Model Swap | Replace JSON state with screenshots + multimodal LLM | Accuracy degradation, inference cost, structured vs. vision comparison |
| M6 | Formal Writeup | Complete analysis document | Cross-milestone comparison, lessons learned |

## 3. Architecture

Three layers with clean interfaces:

```
┌─────────────────────────────────────────────────┐
│                   Game Layer                     │
│  (Pygame VS clone - game logic, rendering)       │
│                                                  │
│  Exposes: GameState (JSON snapshot per tick)      │
│  Accepts: Action (movement direction)            │
└──────────────┬──────────────────▲────────────────┘
               │ state            │ action
               ▼                  │
┌─────────────────────────────────────────────────┐
│                 Agent Layer                       │
│  (Controller that bridges game ↔ LLM)            │
│                                                  │
│  - Serializes game state to prompt               │
│  - Parses LLM response into action               │
│  - Manages step-lock / async loop modes          │
│  - Collects metrics per decision                 │
└──────────────┬──────────────────▲────────────────┘
               │ prompt           │ response
               ▼                  │
┌─────────────────────────────────────────────────┐
│                  LLM Layer                       │
│  (Ollama API — swappable models)                 │
│                                                  │
│  Stage 1: Text model (Llama 3.1 8B)             │
│  Stage 2: Vision model (LLaVA 7B)               │
└─────────────────────────────────────────────────┘
```

### Key Interfaces

```python
# Game → Agent
class GameState:
    player: dict       # {x, y, hp, max_hp, attack_range, attack_cooldown}
    enemies: list      # [{x, y, type, hp, speed, direction}]
    projectiles: list  # [{x, y, dx, dy, damage, friendly}]
    pickups: list      # [{x, y, type}]
    arena: dict        # {width, height, elapsed_time, wave_number}

# Agent → Game
class Action:
    direction: str     # "up", "down", "left", "right", "up-left", etc. or "none"

# Metrics (logged per decision)
class DecisionMetric:
    tick: int
    inference_time_ms: float
    game_state_size: int
    prompt_tokens: int
    completion_tokens: int
    action_chosen: str
    threats_in_range: int
    hp_at_decision: int
```

## 4. Game Mechanics

### Player
- Moves in 8 directions (WASD + diagonals)
- Auto-attacks nearest enemy within range on a cooldown timer
- Has HP, dies at 0
- Collects pickups by walking over them
- No leveling/upgrades in M1

### Enemies (3 types)
- **Swarmers** — weak, fast, move directly toward player (bats)
- **Tanks** — slow, high HP, move toward player (golems)
- **Shooters** — medium speed, stop at range and fire projectiles (mages)
- Spawn in waves from arena edges, increasing density over time

### Projectiles
- Enemy projectiles (from Shooters) — player must dodge
- Player auto-attack is melee range (circle around player), not a projectile

### Pickups
- **Health** — restores HP
- **XP gems** — tracked for scoring/metrics

### Arena
- Fixed rectangular area with boundaries
- Camera follows player
- Simple tiled background

### Win/Lose
- No win condition — survive as long as possible
- Death = run ends, metrics saved
- Score = survival time + XP collected

### Play Modes
- `run_human.py` — WASD controls, same game engine
- `run_ai.py` — LLM controls movement via step-lock
- Same engine, different input source — enables human baseline comparison

## 5. LLM Integration

### Runtime
- **Ollama** — local LLM server, REST API at `http://localhost:11434`
- Stage 1: `llama3.1:8b` (text, fits in 8GB VRAM)
- Stage 2: `llava:7b` or `llama3.2-vision:11b` quantized (vision, fits in 8GB)

### Prompt Strategy (Structured State)

The state serializer converts raw game state into natural language:

```
You are an AI playing a Vampire Survivors-style game. Your character auto-attacks
nearby enemies. You ONLY control movement.

CURRENT STATE:
- Your position: (200, 300), HP: 65/100
- 12 enemies nearby:
  - 3 Swarmers approaching from the NORTH (closest: 45px away)
  - 1 Tank approaching from the WEST (120px away)
  - 2 Shooters to the EAST (200px away, firing projectiles)
- 4 projectiles heading toward you:
  - 2 from the EAST, will reach you in ~15 ticks
  - 2 from the NORTHEAST, will reach you in ~8 ticks
- Pickups: Health potion 180px to the SOUTH
- Arena bounds: 50px from WEST wall

Respond with EXACTLY one direction: up, down, left, right,
up-left, up-right, down-left, down-right, or none.
Think briefly about the biggest threat, then choose.
```

Natural language over raw JSON because LLMs reason better about "3 Swarmers approaching from the NORTH" than coordinate arrays. The serializer does spatial math (distances, relative directions, threat projections) so the LLM focuses on strategy.

### Response Parsing
- Extract direction keyword from LLM response
- Malformed response → default to "none", log as parsing failure
- Chain-of-thought included in prompt for reasoning logs

### API Configuration
- Temperature: 0.3 (consistent decisions)
- `num_predict`: 100 (short response — direction + brief reasoning)
- `stream: False` for step-lock, `stream: True` for async mode

## 6. Metrics & Analysis Framework

### Per-Decision Metrics (every tick)

| Metric | Type | Purpose |
|---|---|---|
| `tick` | int | Game tick number |
| `timestamp` | float | Wall clock time |
| `inference_time_ms` | float | LLM response time |
| `prompt_tokens` | int | Tokens sent |
| `completion_tokens` | int | Tokens received |
| `game_state_size_bytes` | int | Serialized state size |
| `action_chosen` | str | Direction picked |
| `action_parse_success` | bool | Clean parse? |
| `llm_reasoning` | str | Chain-of-thought excerpt |
| `player_hp` | int | HP at decision time |
| `enemies_alive` | int | Total enemies on screen |
| `threats_in_range` | int | Enemies within danger radius |
| `nearest_threat_dist` | float | Closest enemy distance |
| `nearest_pickup_dist` | float | Closest pickup distance |

### Per-Run Summary

| Metric | Purpose |
|---|---|
| `survival_time` | Primary performance measure |
| `total_ticks` | Total decisions made |
| `avg_inference_ms` | Mean LLM response time |
| `p95_inference_ms` | Tail latency |
| `total_xp_collected` | Reward signal proxy |
| `damage_taken` | Dodge effectiveness |
| `parse_failure_rate` | LLM output reliability |
| `tokens_per_run` | Total token cost |

### Storage
- CSV per run in `data/runs/`, one row per tick
- Full game state replay as JSON in `data/replays/`

### Analysis Outputs
- Inference time histogram
- Survival time distribution across N runs
- Action distribution (directional bias)
- HP over time curves
- Player position heatmap
- Decision quality vs. threat proximity scatter
- Human vs. AI baseline comparison

### Writeup Structure (per milestone)
1. **Summary** — milestone goal, what was tested
2. **Setup** — hardware, model, game config, run parameters
3. **Method** — how metrics were collected, number of runs, controls
4. **Results** — tables, charts, key numbers
5. **Discussion** — what worked, what didn't, surprising behaviors
6. **Next Steps** — what the next milestone addresses

## 7. Tech Stack

```
pygame>=2.5.0          # Game engine
requests>=2.31.0       # Ollama API calls
pandas>=2.0.0          # Metrics analysis
matplotlib>=3.7.0      # Charts for writeups
```

External tools (installed separately):
- **Ollama** — local LLM runtime
- **Python 3.10+**

## 8. Hardware

- GPU: NVIDIA RTX 3070 FTW 8GB
- RAM: 64GB DDR5
- CPU: AMD Ryzen 5 5600X 6-Core (3.70 GHz base, ~4.3 GHz boost)

## 9. Directory Structure

```
vampire-survivors-ai/
├── README.md
├── requirements.txt
├── docs/
│   ├── specs/
│   └── analysis/
│       ├── m2-structured-state/
│       ├── m4-async-mode/
│       └── m5-vision-model/
├── src/
│   ├── game/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── player.py
│   │   ├── enemy.py
│   │   ├── projectile.py
│   │   ├── pickup.py
│   │   ├── arena.py
│   │   └── renderer.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── controller.py
│   │   ├── state_serializer.py
│   │   ├── action_parser.py
│   │   └── llm_client.py
│   ├── metrics/
│   │   ├── __init__.py
│   │   ├── collector.py
│   │   ├── replay.py
│   │   └── dashboard.py
│   └── config.py
├── data/
│   ├── runs/
│   └── replays/
└── scripts/
    ├── run_human.py
    ├── run_ai.py
    └── analyze_run.py
```

## 10. Credits & Inspiration

- [Ramp Labs — AI Plays RollerCoaster Tycoon](https://labs.ramp.com/rct)
- [Vampire Survivors](https://store.steampowered.com/app/1794680/Vampire_Survivors/) by poncle
- [The Spell Brigade](https://store.steampowered.com/app/2646460/The_Spell_Brigade/)
- Built with [Claude Code](https://claude.ai/claude-code) by Anthropic
