import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from maze_runner.game import Game

if __name__ == "__main__":
    Game().run()
