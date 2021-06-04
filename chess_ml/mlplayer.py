import time

from chess_ml import perceptron
from board import chess_logic
from chess_ml import util
from tqdm import tqdm


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
        :return:
        """
        return self.color

    def move(self):
        if self.perceptron is None:
            fen = self.board.get_fen()
            self.perceptron = perceptron.Perceptron(fen, "data/weights.npy")

        move_predictions = []
        print("Predicting win-rate for each move")
        # Get current fen data and board-array
        old_fen = self.board.get_fen()
        old_board_array = self.board.get_board_array().copy()
        # Go through every square and predict moves from it
        for i in range(8):
            for j in range(8):
                moves = chess_logic.legal_moves(
                    self.board.get_board_array(),
                    [i, j],
                    self.color,
                    self.board.get_castle(),
                    self.board.get_en_passent()
                )
                for m in moves:
                    if m != [0, 0]:
                        fr = [i, j]
                        to = [fr[0]+m[0], fr[1]+m[1]]
                        # Move piece
                        piece = self.board.get_board_array()[to[0], to[1]].get_content()
                        self.board.move_piece(fr, to)
                        # Update fen
                        self.board.new_fen()
                        show_pr = False
                        if show_pr:
                            self.board.set_fen(self.board.get_fen())
                            self.board.board_array = self.board.set_board_array()
                            self.board.add_pieces()
                            self.board.update_board()
                        # Get fen and predict
                        fen = self.board.get_fen()
                        data = util.get_data(fen)
                        p, activations = self.perceptron.predict(data)
                        if self.color == "b":
                            p = 1 - p
                        move_predictions.append([[a for a in activations], p, [fr, to]])
                        # Update fen
                        self.board.set_fen(old_fen)
                        # Add pieces from old fen to get current board
                        self.board.board_array = self.board.set_board_array()
                        self.board.add_pieces()

        print("Deciding move")
        move = util.decide_from_predictions(move_predictions)
        if self.color == "w":
            print("Prediction: {:.2f}".format((move[1] * 200) - 100))
        elif self.color == "b":
            print("Prediction: {:.2f}".format(((1 - move[1]) * 200) - 100))

        # Add selected move, data and probability to game history
        #   for updating when game is finished
        self.game_history.append(move)

        # Extract squares to move from and to
        move_from = move[2][0]
        move_to = move[2][1]
        no_move = True
        for i in range(len(move_from)):
            if move_from[i] != move_to[i]:
                no_move = False
        if no_move:
            raise Exception("Moves are equal")
        return move_from, move_to

    def promote_pawn(self):
        fen = self.board.get_fen()
        if self.promote_perceptron is None:
            self.promote_perceptron = perceptron.Perceptron(fen, "data/promote_weights.npy")

        promote_predictions = []

        print("Predicting win-rate for promoting pawn")
        promotions = []
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
        print("Deciding promotion")
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

    def learn_pos(self, target):
        """
        Go back through game and learn from it
        :param target: win, loss or draw
        :return: weight_list
        """
        new_weight_list = []
        for i in tqdm(range(len(self.game_history))):
            predict = self.game_history[i][1]
            if self.color == "b":
                predict = 1 - predict
            new_weight_list.append(self.perceptron.back_prop(self.game_history[i][0], predict, target))
        return new_weight_list

    def learn_prom(self, target):
        """
        Go back through promotions in game and learn from it
        :param target: win, loss or draw
        :return: weight_list
        """
        new_prom_list = []
        for i in tqdm(range(len(self.promote_history))):
            predict = self.promote_history[i][1]
            if self.color == "b":
                predict = 1 - predict
            new_prom_list.append(self.promote_perceptron.back_prop(self.promote_history[i][0], predict, target))
        return new_prom_list

