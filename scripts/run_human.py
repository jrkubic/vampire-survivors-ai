# scripts/run_human.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.game.main import Game

if __name__ == "__main__":
    game = Game()
    game.run_human()
