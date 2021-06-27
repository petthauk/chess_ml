import copy
import sys

from chess_ml import perceptron, position_nodes
from board import chess_logic
import util.util as util
from tqdm import tqdm
import time
import numpy as np


def sort_node_func(e):
    return e.get_sort_prediction()


def finished_game(status):
    """
    Checks if game is finished
    :param status:
    :return: True if game is finished, false if not
    """
    return status in ["w", "b", "d"]


def finished_prediction(status):
    """
    Gets prediction of finished game
    :param status:
    :return: 1.0 if white wins, 0.0 if black wins, 0.5 if draw
    """
    finished_dict = {"w": 1.0, "b": 0.0, "d": 0.5}
    return finished_dict[status]


class MlPlayer:
    def __init__(self, color, board, p_tron=None, promote_p_tron=None):
        self.color = color
        self.perceptron = p_tron
        self.promote_perceptron = promote_p_tron
        self.board = board
        self.game_history = []
        self.promote_history = []

    def get_color(self):
        """
        Returns color
        :return: self.color (String)
        """
        return self.color

    def move_min_max(self):
        fen = self.board.get_fen()
        if self.perceptron is None:
            self.perceptron = perceptron.Perceptron(fen, "data/weights.npy")
        data = util.get_data(fen)
        p, a = self.perceptron.predict(data)
        root = position_nodes.Node(p, a, fen, self.board.get_bw(), None, p*10)
        self.BFS(root, time.time())
        print("Minimax")
        if self.color == "w":
            move_node = self.minimax(root, -0.1, 1.1, True)
        else:
            move_node = self.minimax(root, 1.1, -0.1, False)

        self.board.set_status("-")
        self.board.set_fen(root.get_fen())
        self.board.board_array = self.board.set_board_array()
        self.board.add_pieces()

        self.board.move_piece(move_node.get_move()[0], move_node.get_move()[1])
        self.board.new_fen()

        fen = self.board.get_fen()
        data = util.get_data(fen)
        p, a = self.perceptron.predict(data)

        if p - move_node.get_prediction() != 0.0:
            print("Predicted value: {}".format(p))
            print("Target value:    {}".format(move_node.get_prediction()))
            self.perceptron.weights = self.perceptron.back_prop(
                a,
                p,
                move_node.get_prediction()
            )

            print("Saving weights")
            util.save_weights(
                np.array(self.perceptron.weights, dtype=object),
                "data/weights.npy"
            )
            util.save_weights(
                np.array(self.promote_perceptron.weights, dtype=object),
                "data/promote_weights.npy"
            )

        self.board.set_status("-")
        self.board.set_fen(root.get_fen())
        self.board.board_array = self.board.set_board_array()
        self.board.add_pieces()

        print("\nChoosing move with prediction: {}\n".format(move_node.get_prediction()))
        return move_node.get_move()[0], move_node.get_move()[1], move_node.get_promote()

    def BFS(self, root, tic):
        """
        Breadth first search to get tree of positions
        :return:
        """
        depth = 1
        print("Depth: {}".format(depth))
        color = self.board.get_bw()
        full_move = self.board.get_full_move()
        node_list = [root]
        while len(node_list) > 0:
            node = node_list.pop(0)
            self.board.set_fen(node.get_fen())
            self.board.board_array = self.board.set_board_array()
            self.board.add_pieces()
            self.board.win_lose_draw()

            if self.board.get_status() != "-":
                continue
            toc = time.time()
            if toc - tic > 60.0:
                return

            # Get node-prediction for sorting on prediction
            fen = self.board.get_fen()
            data = util.get_data(fen)
            node_prediction, _ = self.perceptron.predict(data)

            if self.board.get_bw() == "b":
                node_prediction = 1.0 - node_prediction

            new_full_move = self.board.get_full_move()
            new_depth = (new_full_move - full_move) * 2 + 1
            if color == "w" and self.board.get_bw() == "b":
                new_depth += 1
            elif color == "b" and self.board.get_bw() == "w":
                new_depth -= 1
            if new_depth != depth:
                depth = new_depth
                print("Depth: {}".format(depth))

            move_list = []
            for row in range(8):
                for col in range(8):
                    fr = [row, col]
                    moves = chess_logic.legal_moves(
                        self.board.get_board_array(),
                        fr,
                        self.board.get_bw(),
                        self.board.get_castle(),
                        self.board.get_en_passent()
                    )

                    br_out = False
                    for m in moves:
                        to = [fr[0] + m[0], fr[1] + m[1]]

                        # Move piece
                        self.board.move_piece(fr, to)

                        if self.board.get_promoting():
                            for piece in ["q", "r", "b", "n"]:
                                self.board.promote_pawn(to, piece)
                                self.board.next_turn(visual=False)
                                p, a, fen = self.predict_pos()

                                move_list.append([[fr, to], p, a, fen, self.board.get_bw(), piece])

                                if p == 1.0:
                                    br_out = True

                                self.board.set_status("-")
                                self.board.positions_in_game[self.board.get_fen_pos()] -= 1

                                if br_out:
                                    break
                        else:
                            self.board.next_turn(visual=False)
                            p, a, fen = self.predict_pos()

                            move_list.append([[fr, to], p, a, fen, self.board.get_bw(), None])

                            if p == 1.0:
                                br_out = True

                            self.board.set_status("-")
                            self.board.positions_in_game[self.board.get_fen_pos()] -= 1

                        self.board.set_fen(node.get_fen())
                        self.board.board_array = self.board.set_board_array()
                        self.board.add_pieces()

                        if br_out:
                            break

            # Add moves and positions from move list to node_list and position-tree
            for m in move_list:
                fr = m[0][0]
                to = m[0][1]
                p = m[1]
                a = m[2]
                fen = m[3]
                bw = m[4]
                promote_piece = m[5]

                child = position_nodes.Node(
                    p, a, fen, bw, promote_piece, ((node_prediction * 10) + (p - node_prediction))
                )
                node.add_child(child, [fr, to], self.board.get_bw())
                node_list.append(child)

            # Sort node_list so it always checks the node with the greatest prediction next
            if color == "w":
                node_list.sort(key=sort_node_func, reverse=True)
            elif color == "b":
                node_list.sort(key=sort_node_func)

    def minimax(self, position, alpha, beta, maximizing_player):
        """
        Minimax-algorithm with alpha-beta pruning
        :return:
        """
        if position.get_bw() == "w":
            position.set_prediction(1.0 - position.get_prediction())

        if len(position.get_children()) == 0:
            return position

        ret_pos = position

        if maximizing_player:
            max_eval = -0.1
            for child in position.get_children():
                pos = self.minimax(child, alpha, beta, False)
                eval = pos.get_prediction()
                if eval >= max_eval:
                    max_eval = eval
                    ret_pos = child
                    ret_pos.set_prediction(eval)
                alpha2 = max(alpha, eval)
                if beta <= alpha2:
                    break
        else:
            min_eval = 1.1
            for child in position.get_children():
                pos = self.minimax(child, alpha, beta, True)
                eval = pos.get_prediction()
                if eval <= min_eval:
                    min_eval = eval
                    ret_pos = child
                    ret_pos.set_prediction(eval)
                beta2 = min(beta, eval)
                if beta2 <= alpha:
                    break
        return ret_pos

    def promote_pawn(self):
        fen = self.board.get_fen()
        if self.promote_perceptron is None:
            self.promote_perceptron = perceptron.Perceptron(fen, "data/promote_weights.npy")

        promote_predictions = []

        if self.board.get_bw() == "w":
            promotions = ["N", "B", "R", "Q"]
        else:
            promotions = ["n", "b", "r", "q"]
        for p in promotions:
            data = util.get_promote_data(fen, p)
            predict, activations = self.promote_perceptron.predict(data)
            if self.color == "b":
                predict = 1 - predict
            promote_predictions.append([[a for a in activations], predict])
        promotion = util.decide_from_predictions(promote_predictions)

        self.promote_history.append(promotion)
        promote_piece = ""
        if promotion[0][0][-8] == 1:
            promote_piece = "n"
        if promotion[0][0][-7] == 1:
            promote_piece = "n"
        if promotion[0][0][-6] == 1:
            promote_piece = "b"
        if promotion[0][0][-5] == 1:
            promote_piece = "b"
        if promotion[0][0][-4] == 1:
            promote_piece = "r"
        if promotion[0][0][-3] == 1:
            promote_piece = "r"
        if promotion[0][0][-2] == 1:
            promote_piece = "q"
        if promotion[0][0][-1] == 1:
            promote_piece = "q"
        return promote_piece

    def predict_pos(self):
        # Get fen and predict
        fen = self.board.get_fen()
        data = util.get_data(fen)
        p, a = self.perceptron.predict(data)

        if finished_game(self.board.get_status()):
            p = finished_prediction(self.board.get_status())

        if self.board.get_bw() == "w":
            p = 1.0 - p

        return p, a, fen
