import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.game.main import Game
from src.agent.controller import StepLockController
from src.agent.llm_client import OllamaClient

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run AI-controlled Vampire Survivors")
    parser.add_argument("--no-render", action="store_true", help="Run without rendering (faster)")
    parser.add_argument("--max-ticks", type=int, default=None, help="Max ticks before stopping")
    parser.add_argument("--model", type=str, default=None, help="Ollama model override")
    args = parser.parse_args()

    game = Game()
    client = OllamaClient()
    if args.model:
        client.model = args.model

    controller = StepLockController(game=game, client=client)
    print(f"Starting AI run with model: {client.model}")
    print(f"Render: {not args.no_render}")
    print("Press ESC to stop early.\n")

    controller.run(max_ticks=args.max_ticks, render=not args.no_render)
