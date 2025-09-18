import pygame
import random
import sys

from game import Game
from ai import Random, MinMax, AlphaBeta


def main():
    random.seed(42)

    pygame.init()
    pygame.display.set_caption("Kalah Game")

    game = Game()
    # Set the AI for player 0 and player 1, respectively
    game.set_ai_players(Random, AlphaBeta)
    game.initialize()

    game.run()

    pygame.quit()

if __name__ == "__main__":
    main()
    sys.exit()

