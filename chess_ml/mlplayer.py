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
        :return: self.color (String)
        """
        return self.color

    def move(self, show_moves=False):
        """
        Gets prediction for each move from current position and chooses one of those moves.
        :param show_moves: Boolean to say if we should see all moves that is considered. Default is False.
        :return: A tuple containing square to move from a square to move to
        """
        # If perceptron isn't initialized, initialize it.
        if self.perceptron is None:
            fen = self.board.get_fen()
            self.perceptron = perceptron.Perceptron(fen, "data/weights.npy")

        # A list which will contain all possible moves with predictions for them.
        move_predictions = []

        # Predict win-rate for current position and put in move_predictions
        # Get current fen-data
        old_fen = self.board.get_fen()

        # Get data
        data = util.get_data(old_fen)
        if data[-1] != 1 or self.color != "w":
            p, activations = self.perceptron.predict(data)
            if self.color == "b":
                p = 1.0 - p
            self.game_history.append(
                [[a for a in activations], p]
            )

        print("Predicting win-rate for each move")
        # Go through every square and predict moves from it
        for i in range(8):
            for j in range(8):
                # Set square to move from
                fr = [i, j]

                # Get legal moves from current square
                moves = chess_logic.legal_moves(
                    self.board.get_board_array(),
                    [i, j],
                    self.color,
                    self.board.get_castle(),
                    self.board.get_en_passent()
                )

                # Go through every move
                for m in moves:
                    if m != [0, 0]:
                        # Set square to move to
                        to = [fr[0]+m[0], fr[1]+m[1]]

                        # Move piece
                        self.board.move_piece(fr, to)

                        # Update fen
                        self.board.new_fen()

                        # If we want to see all moves predicted
                        if show_moves:
                            self.board.set_fen(self.board.get_fen())
                            self.board.board_array = self.board.set_board_array()
                            self.board.add_pieces()
                            self.board.update_board()

                        # Get fen and predict
                        fen = self.board.get_fen()
                        data = util.get_data(fen)
                        p, activations = self.perceptron.predict(data)

                        # If it is blacks turn to move. Flip prediction.
                        # Black wants to be as close to 0.0 as possible.
                        if self.color == "b":
                            p = 1 - p

                        # Add activations, prediction and move to list of moves
                        move_predictions.append([[a for a in activations], p, [fr, to]])

                        # Set fen to old fen for predicting new move or 
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
        eta_list = []
        # Go through game and update weights
        for i in tqdm(range(len(self.game_history))):
            predict = self.game_history[i][1]
            eta = abs(predict-target)
            if eta > 1.0:
                eta = 1.0
            eta_list.append(eta)
            if self.color == "b":
                predict = 1 - predict
            new_weight_list.append(
                self.perceptron.back_prop(
                    self.game_history[i][0],
                    predict,
                    target,
                    eta=eta
                )
            )
        tot_eta = 0
        for eta in eta_list:
            tot_eta += eta
        mean_eta = tot_eta / len(eta_list)
        print("\nMean ETA: {:.2f}\n".format(mean_eta))
        return new_weight_list

    def learn_prom(self, target):
        """
        Go back through promotions in game and learn from it
        :param target: win, loss or draw
        :return: weight_list
        """
        new_prom_list = []
        eta_list = []
        if len(self.promote_history) > 0:
            # Go through promoting and update weights
            for i in tqdm(range(len(self.promote_history))):
                predict = self.promote_history[i][1]
                eta = abs(predict-target)
                if eta > 1.0:
                    eta = 1.0
                eta_list.append(eta)
                if self.color == "b":
                    predict = 1 - predict
                new_prom_list.append(
                    self.promote_perceptron.back_prop(
                        self.promote_history[i][0],
                        predict,
                        target,
                        eta=eta
                    )
                )
            tot_eta = 0
            for eta in eta_list:
                tot_eta += eta
            mean_eta = tot_eta / len(eta_list)
            print("\nMean ETA: {:.2f}\n".format(mean_eta))
        return new_prom_list

