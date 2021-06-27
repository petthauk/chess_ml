from board import game
from chess_ml import mlplayer
import util.util as util
import pygame as pg
from pygame.locals import *
import numpy as np
from chess_ml.perceptron import Perceptron


def run(b, move_perceptron, promote_perceptron, players):
    """
    Run one game
    :param b: Board
    :param move_perceptron: Perceptron for moving
    :param promote_perceptron: Perceptron for promoting
    :param players: List of two players
    :return:
    """
    move_from = []
    move_to = []
    main_loop = True
    promote = None
    while main_loop:
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                main_loop = False
                break
            if b.get_status() == "-":
                color = b.get_bw()
                if (
                        (color == "w" and players[0].get_color() == "h")
                        or
                        (color == "b" and players[1].get_color() == "h")
                ):
                    if event.type == MOUSEBUTTONDOWN:
                        pos = pg.mouse.get_pos()
                        for r in b.get_board_array():
                            for square in r:
                                if square.get_visual().collidepoint(pos):
                                    square.click()
                        b.update_board()
                    if event.type == KEYDOWN:
                        if event.key == K_r:  # Resign
                            print("Player resigning")
                            if color == "w":
                                print("Black wins")
                                b.set_status("b")
                            if color == "b":
                                print("White wins")
                                b.set_status("w")
                        if event.key == K_d:  # Ask for draw
                            print("Player asking for draw")
                            if (
                                    (color == "w" and players[1].get_color() == "b")
                                    or
                                    (color == "b" and players[0].get_color() == "w")
                                ):  # Asking computer for draw
                                fen = b.get_fen()
                                data = util.get_data(fen)
                                perceptron = Perceptron(fen, "data/weights.npy")
                                win_prob, _ = perceptron.predict(data)
                                if color == "w":
                                    win_prob = 1 - win_prob
                                if win_prob < 0.5:
                                    print("Accepting draw")
                                    b.set_status("d")
                                else:
                                    print("Draw rejected. Continue playing or resign (r)")
                            else:  # Two humans are playing
                                pass

                else:
                    if b.get_bw() == "w" and players[0].get_color() == "w":
                        move_from, move_to, promote = players[0].move_min_max()
                        b.move_piece(move_from, move_to)

                    elif b.get_bw() == "b" and players[1].get_color() == "b":
                        move_from, move_to, promote = players[1].move_min_max()
                        b.move_piece(move_from, move_to)

                    print("Move from {} to {}".format(
                        util.array_position_to_string_position(move_from),
                        util.array_position_to_string_position(move_to)
                    ))

                    if promote is not None:
                        b.promote_pawn(move_to, promote)

                    b.next_turn()

                    if len(pg.event.get()) < 2:
                        pg.event.post(pg.event.Event(MOUSEMOTION))

                    print(b.get_fen())
                    print()
                    print(b)

                    if color == "w":
                        print("Black to move!!!")
                    elif color == "b":
                        print("White to move!!!")
                    else:
                        raise Exception("Color to move isn't \"w\" or \"b\"")

            else:
                print("Game finished! Trying to learn from it")
                print("Learning last position")
                fen = b.get_fen()
                data = util.get_data(fen)
                p, a = move_perceptron.predict(data)
                if b.get_status() == "w":
                    target_p = 1.0
                elif b.get_status() == "b":
                    target_p = 0.0
                else:
                    target_p = 0.5
                move_perceptron.weights = move_perceptron.back_prop(
                    a,
                    p,
                    target_p
                )
                print("Saving weights")
                util.save_weights(move_perceptron.weights, "data/weights.npy")

                pg.event.clear()
                pg.event.post(pg.event.Event(QUIT))
                # Update game_log
                util.update_game_log(b.get_status())
                pg.quit()
                main_loop = False
                break


def main():
    """
    Starts new game
    :return:
    """
    while True:  # Infinite games
        print("Starting new game")
        g = game.Game()
        b = g.get_board()
        move_perceptron = Perceptron(b.get_fen(), "data/weights.npy")
        promote_perceptron = Perceptron(b.get_fen(), "data/promote_weights.npy")
        run(b, move_perceptron, promote_perceptron, players=[
            mlplayer.MlPlayer("w", b, p_tron=move_perceptron, promote_p_tron=promote_perceptron),
            mlplayer.MlPlayer("b", b, p_tron=move_perceptron, promote_p_tron=promote_perceptron)
        ])


if __name__ == "__main__":
    main()
