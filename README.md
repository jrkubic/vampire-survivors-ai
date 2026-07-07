# Vampire Survivors AI

A Pygame Vampire Survivors clone with a locally-run LLM agent that plays the game autonomously.

Built as a personal learning project to explore the fundamentals of implementing, integrating, and analyzing a local AI model as a game-playing agent — watching how an LLM handles spatial reasoning, threat assessment, and real-time decision-making.

## Overview

The project progresses through stages:

1. **Pygame VS Clone** — A minimal Vampire Survivors-style game: auto-attacking player, enemy waves, projectiles, pickups
2. **Step-Lock AI (Structured State)** — LLM receives JSON game state, reasons about threats, outputs movement direction
3. **Metrics & Analysis** — Per-decision logging, replay system, formal performance writeups
4. **Async Real-Time Mode** — AI plays in real-time without pausing the game
5. **Vision Model Swap** — Replace structured state with screenshots + multimodal LLM
6. **Formal Writeup** — Cross-milestone analysis comparing approaches

## Architecture

```
Game Layer (Pygame)  →  Agent Layer (Controller)  →  LLM Layer (Ollama)
  exports GameState        serializes to prompt         Llama 3.1 8B (text)
  accepts Action           parses response              LLaVA 7B (vision)
```

The game exposes its full state (player position, enemy positions, projectiles, pickups) each tick. The agent layer translates this into a natural language prompt, sends it to a local LLM via Ollama, and parses the response into a movement direction.

## Tech Stack

- **Python 3.10+** with **Pygame** for the game
- **Ollama** for local LLM inference
- **Llama 3.1 8B** (structured state) / **LLaVA 7B** (vision)
- **pandas** + **matplotlib** for metrics and analysis

## Hardware

Developed and benchmarked on:
- GPU: NVIDIA RTX 3070 8GB
- RAM: 64GB DDR5
- CPU: AMD Ryzen 5 5600X (6-core)

## Setup

```bash
git clone https://github.com/jrkubic/vampire-survivors-ai.git
cd vampire-survivors-ai
pip install -r requirements.txt

# Install Ollama: https://ollama.com
ollama pull llama3.1:8b
```

## Usage

```bash
# Play the game yourself
python scripts/run_human.py

# Let the AI play (step-lock mode)
python scripts/run_ai.py

# Analyze a run
python scripts/analyze_run.py data/runs/<run_id>.csv
```

## Credits & Inspiration

- [Ramp Labs — AI Plays RollerCoaster Tycoon](https://labs.ramp.com/rct) — Inspiration for integrating an LLM as a game-playing agent
- [Vampire Survivors](https://store.steampowered.com/app/1794680/Vampire_Survivors/) by poncle — The game this project clones
- [The Spell Brigade](https://store.steampowered.com/app/2646460/The_Spell_Brigade/) — Additional genre inspiration
- Built with [Claude Code](https://claude.ai/claude-code) by Anthropic

## License

MIT
