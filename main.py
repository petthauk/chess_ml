from board import game
from chess_ml import mlplayer
from chess_ml import util
import pygame as pg
from pygame.locals import *
import numpy as np


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
                elif b.get_bw() == "w" and players[0].get_color() == "w":
                    move_from, move_to = players[0].move()
                    b.move_piece(move_from, move_to)
                    if b.get_promoting():
                        b.promote_pawn(move_to, players[0].promote_pawn())
                    if len(pg.event.get()) < 2:
                        pg.event.post(pg.event.Event(MOUSEMOTION))
                elif b.get_bw() == "b" and players[1].get_color() == "b":
                    move_from, move_to = players[1].move()
                    b.move_piece(move_from, move_to)
                    if b.get_promoting():
                        b.promote_pawn(move_to, players[1].promote_pawn())
                    if len(pg.event.get()) < 2:
                        pg.event.post(pg.event.Event(MOUSEMOTION))
            else:
                print("Game finished! Trying to learn from it")
                status = game_outcome_dict[b.get_status()]
                if players[0].get_color() == "w":
                    for wl in players[0].learn_pos(status):
                        weight_list.append(wl)
                    for pl in players[0].learn_prom(status):
                        promote_list.append(pl)
                if players[1].get_color() == "b":
                    for wl in players[1].learn_pos(status):
                        weight_list.append(wl)
                    for pl in players[1].learn_prom(status):
                        promote_list.append(pl)
                pg.event.clear()
                pg.event.post(pg.event.Event(QUIT))

    print("Updating weights")
    # Find mean of all weights and save new weights
    weight_list.append(util.get_weights("data/weights.npy"))
    new_weights = [
        np.zeros(weight_list[0][0].shape),
        np.zeros(weight_list[0][1].shape)
    ]
    for a in range(len(weight_list[0])):
        for i in range(weight_list[0][a].shape[0]):
            for j in range(weight_list[0][a].shape[1]):
                tot = 0.0
                for k in range(len(weight_list)):
                    tot += weight_list[k][a][i][j]
                new_weights[a][i][j] = tot / len(weight_list)
    util.save_weights(np.array(new_weights, dtype=object), "data/weights.npy")

    print("Updating promote weights")
    # Find mean of all promote-weights and save new weights
    promote_list.append(util.get_weights("data/promote_weights.npy"))
    new_promote = [
        np.zeros(promote_list[0][0].shape),
        np.zeros(promote_list[0][1].shape)
    ]
    for a in range(len(promote_list[0])):
        for i in range(promote_list[0][a].shape[0]):
            for j in range(promote_list[0][a].shape[1]):
                tot = 0.0
                for k in range(len(promote_list)):
                    tot += promote_list[k][a][i][j]
                new_promote[a][i][j] = tot / len(promote_list)
    util.save_weights(np.array(new_promote, dtype=object), "data/promote_weights.npy")


def main():
    for _ in range(1000):
        print("Starting new game")
        g = game.Game()
        b = g.get_board()
        white_player = mlplayer.MlPlayer("w", b)
        black_player = mlplayer.MlPlayer("b", b)
        human_player = mlplayer.MlPlayer("h", b)
        run(b, players=[white_player, black_player])


if __name__ == "__main__":
    main()
