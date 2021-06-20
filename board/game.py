import pygame as pg
from pygame.locals import *
import sys
import board.chess_board as board


w = 60 * 8
h = 60 * 8


class Game:
    """
    Class to setup and start a game
    """
    def __init__(self):
        self.b = board.Board(w, h)

    def get_board(self):
        """
        Returns board
        :return: Board-class
        """
        return self.b

    def run(self):
        """
        Where the game is created and launched
        :return:
        """
        # While loop to show display
        while True:
            for event in pg.event.get():
                # Quitting game
                if event.type == QUIT:
                    pg.quit()
                    sys.exit()
                # If game can continue
                if self.b.get_status() == "-":
                    # Pressing mouse
                    if event.type == MOUSEBUTTONDOWN:
                        pos = pg.mouse.get_pos()
                        for r in self.b.get_board_array():
                            for square in r:
                                if square.get_visual().collidepoint(pos):
                                    square.click()
                        self.b.update_board()


if __name__ == "__main__":
    # Launch main-function if running this script
    game = Game()
    game.run()
