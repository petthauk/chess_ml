from time import sleep
from board import game
from board import util as board_util
from chess_ml import mlplayer
from chess_ml import util
import pygame as pg
from pygame.locals import *
import numpy as np
from chess_ml.perceptron import Perceptron


def run(b, players):
    game_outcome_dict = {"w": 1.0, "b": 0.0, "d": 0.5}
    weight_list = []
    promote_list = []
    main_loop = True
    while main_loop:
        for event in pg.event.get():
            if event.type == QUIT:
                pg.quit()
                main_loop = False
                break
            if b.get_status() == "-":
                if (
                        (b.get_bw() == "w" and players[0].get_color() == "h")
                        or
                        (b.get_bw() == "b" and players[1].get_color() == "h")
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
                            if b.get_bw() == "w":
                                print("Black wins")
                                b.set_status("b")
                            if b.get_bw() == "b":
                                print("White wins")
                                b.set_status("w")
                        if event.key == K_d:  # Ask for draw
                            print("Player asking for draw")
                            if (
                                    (b.get_bw() == "w" and players[1].get_color() == "b")
                                    or
                                    (b.get_bw() == "b" and players[0].get_color() == "w")
                                ):  # Asking computer for draw
                                fen = b.get_fen()
                                data = util.get_data(fen)
                                perceptron = Perceptron(fen, "data/weights.npy")
                                win_prob, _ = perceptron.predict(data)
                                if b.get_bw() == "w":
                                    win_prob = 1 - win_prob
                                if win_prob < 0.5:
                                    print("Accepting draw")
                                    b.set_status("d")
                                else:
                                    print("Draw rejected. Continue playing or resign (r)")
                            else:  # Two humans are playing
                                pass

                elif b.get_bw() == "w" and players[0].get_color() == "w":
                    move_from, move_to = players[0].move()
                    b.move_piece(move_from, move_to)
                    print("Move from {} to {}".format(
                        board_util.array_position_to_string_position(move_from),
                        board_util.array_position_to_string_position(move_to)
                    ))
                    if b.get_promoting():
                        promote = players[0].promote_pawn()
                        b.promote_pawn(move_to, promote)
                    b.next_turn()
                    if len(pg.event.get()) < 2:
                        pg.event.post(pg.event.Event(MOUSEMOTION))
                elif b.get_bw() == "b" and players[1].get_color() == "b":
                    move_from, move_to = players[1].move()
                    b.move_piece(move_from, move_to)
                    print("Move from {} to {}".format(
                        board_util.array_position_to_string_position(move_from),
                        board_util.array_position_to_string_position(move_to)
                    ))
                    if b.get_promoting():
                        promote = players[1].promote_pawn()
                        b.promote_pawn(move_to, promote)
                    b.next_turn()
                    if len(pg.event.get()) < 2:
                        pg.event.post(pg.event.Event(MOUSEMOTION))
            else:
                print("Game finished! Trying to learn from it")
                pg.event.clear()
                pg.event.post(pg.event.Event(QUIT))
                # Update game_log
                util.update_game_log(b.get_status())

    status = game_outcome_dict[b.get_status()]
    if players[0].get_color() == "w":
        print("White")
        pos = players[0].learn_pos(status)
        prom = players[0].learn_prom(status)
        for wl in pos:
            weight_list.append(wl)
        for pl in prom:
            promote_list.append(pl)
    if players[1].get_color() == "b":
        print("Black")
        pos = players[1].learn_pos(status)
        prom = players[1].learn_prom(status)
        for wl in pos:
            weight_list.append(wl)
        for pl in prom:
            promote_list.append(pl)

    print("Updating weights")
    # Find mean of all weights and save new weights
    new_weights = [
        np.zeros(weight_list[0][i].shape) for i in range(len(weight_list[0]))
    ]
    for a in range(len(weight_list[0])):
        for i in range(weight_list[0][a].shape[0]):
            for j in range(weight_list[0][a].shape[1]):
                tot = 0.0
                for k in range(len(weight_list)):
                    tot += weight_list[k][a][i][j]
                new_weights[a][i][j] = tot / len(weight_list)
    util.save_weights(np.array(new_weights, dtype=object), "data/weights.npy")
    print()

    print("Updating promote weights")
    # Find mean of all promote-weights and save new weights
    if len(promote_list) > 0:
        new_promote = [
            np.zeros(promote_list[0][i].shape) for i in range(len(promote_list[0]))
        ]
        for a in range(len(promote_list[0])):
            for i in range(promote_list[0][a].shape[0]):
                for j in range(promote_list[0][a].shape[1]):
                    tot = 0.0
                    for k in range(len(promote_list)):
                        tot += promote_list[k][a][i][j]
                    new_promote[a][i][j] = tot / len(promote_list)
        util.save_weights(np.array(new_promote, dtype=object), "data/promote_weights.npy")
    print()


def main():
    while True:
        print("Starting new game")
        g = game.Game()
        b = g.get_board()
        move_perceptron = Perceptron(b.get_fen(), "data/weights.npy")
        promote_perceptron = Perceptron(b.get_fen(), "data/promote_weights.npy")
        run(b, players=[
            mlplayer.MlPlayer("w", b, p_tron=move_perceptron, promote_p_tron=promote_perceptron),
            mlplayer.MlPlayer("b", b, p_tron=move_perceptron, promote_p_tron=promote_perceptron)
        ])


if __name__ == "__main__":
    main()
