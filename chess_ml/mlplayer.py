from chess_ml import perceptron
from board import chess_logic
from chess_ml import util


class MlPlayer:
    def __init__(self, color, board):
        self.color = color
        self.perceptron = None
        self.promote_perceptron = None
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
        fen = self.board.get_fen()
        if self.perceptron is None:
            self.perceptron = perceptron.Perceptron(fen, "data/weights.npy")

        move_predictions = []
        print("Predicting win-rate for each move")
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
                    data = util.get_data(fen, [i, j], m)
                    p, activations = self.perceptron.predict(data)
                    if self.color == "b":
                        p = 1 - p
                    move_predictions.append([[data, activations], p])
        print("Deciding move")
        move = util.decide_from_predictions(move_predictions)

        # Add selected move, data and probability to game history
        #   for updating when game is finished
        self.game_history.append(move)

        # Extract squares to move from and to
        move_from = [move[0][0][-4], move[0][0][-3]]
        move_to = [move[0][0][-2], move[0][0][-1]]
        return move_from, move_to

    def promote_pawn(self):
        fen = self.board.get_fen()
        if self.promote_perceptron is None:
            self.promote_perceptron = perceptron.Perceptron(fen, "data/promote_weights.npy")

        promote_predictions = []

        print("Predicting win-rate for promoting pawn")
        promotions = ["n", "b", "r", "q"]
        for p in promotions:
            data = util.get_promote_data(fen, p)
            predict, activations = self.promote_perceptron.predict(data)
            if self.color == "b":
                predict = 1 - predict
            promote_predictions.append([[data, activations], predict])
        print("Deciding promotion")
        promotion = util.decide_from_predictions(promote_predictions)

        self.promote_history.append(promotion)
        promote_piece = ""
        if promotion[0][0][-1] == util.KNIGHT:
            promote_piece = "n"
        if promotion[0][0][-1] == util.BISHOP:
            promote_piece = "b"
        if promotion[0][0][-1] == util.ROOK:
            promote_piece = "r"
        if promotion[0][0][-1] == util.QUEEN:
            promote_piece = "q"
        return promote_piece

    def learn_pos(self, target):
        """
        Go back through game and learn from it
        :param target: win, loss or draw
        :return: weight_list
        """
        new_weight_list = []
        for pos in self.game_history:
            predict = pos[1]
            if self.color == "b":
                predict = 1 - predict
            new_weight_list.append(self.perceptron.back_prop(pos[0], predict, target))
        return new_weight_list

    def learn_prom(self, target):
        """
        Go back through promotions in game and learn from it
        :param target: win, loss or draw
        :return: weight_list
        """
        new_prom_list = []
        for prom in self.promote_history:
            predict = prom[1]
            if self.color == "b":
                predict = 1 - predict
            new_prom_list.append(self.promote_perceptron.back_prop(prom[0], predict, target))
        return new_prom_list

