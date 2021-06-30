from chess_ml import perceptron, position_nodes
from board import chess_logic
import util.util as util
import time
import numpy as np


def sort_node_func(e):
    """
    Function for helping to sort node_list
    :param e: (Node) element in list
    :return: (Float) sort_prediction
    """
    return e.get_sort_prediction()


def sort_children_func(e):
    """
    Function for helping to sort children of a Node
    :param e: (Node) child of Node
    :return: (Float) prediction
    """
    return e.get_prediction()


def finished_game(status):
    """
    Checks if game is finished
    :param status: (String) Status of game
    :return: (boolean) True if game is finished, false if not
    """
    return status in ["w", "b", "d"]


def finished_prediction(status):
    """
    Gets prediction of finished game
    :param status: (String) Status of game
    :return: (Float) 1.0 if white wins, 0.0 if black wins, 0.5 if draw
    """
    finished_dict = {"w": 1.0, "b": 0.0, "d": 0.5}
    return finished_dict[status]


class MlPlayer:
    """
    Player-class
    """
    def __init__(self, color, board, p_tron=None):
        self.color = color
        self.perceptron = p_tron
        self.board = board
        self.move_list = []
        self.predict_time = []

    def get_color(self):
        """
        Returns color
        :return: self.color (String)
        """
        return self.color

    def move_min_max(self):
        """
        Using Breadth-First-Search to build tree that minimax decides move from.
        :return: move_from([row, col]), move_to ([row, col]), promote (Piece to promote to or None if not promoting)
        """
        # Get fen from current board-position
        fen = self.board.get_fen()

        # If perceptron is not initialized. Initialize it
        if self.perceptron is None:
            self.perceptron = perceptron.Perceptron(fen, "data/weights.npy")

        # Get data from fen and predict game
        data = util.get_data(fen)
        p, a = self.perceptron.predict(data)

        # Make root-node (Current position)
        root = position_nodes.Node(p, a, fen, self.board.get_bw(), None, p*10)

        # Breadth-First-Search to make tree of positions from root-node
        self.BFS(root, time.time())
        mean_predict = np.mean(self.predict_time)
        print("Mean predict time: {} seconds".format(mean_predict))

        # Using minimax to get best node to move to
        print("Minimax")
        if self.color == "w":
            move_node = self.minimax(root, -0.1, 1.1, True)
        else:
            move_node = self.minimax(root, -0.1, 1.1, False)

        # Reset board to root-position for moving to the chosen position
        self.board.set_status("-")
        self.board.set_fen(root.get_fen())
        self.board.board_array = self.board.set_board_array()
        self.board.add_pieces()

        # Move to the chosen position and update fen
        self.board.move_piece(move_node.get_move()[0], move_node.get_move()[1])
        self.board.new_fen()

        # Predict outcome of position we moved to for backpropagation
        fen = self.board.get_fen()
        data = util.get_data(fen)
        p, a = self.perceptron.predict(data)

        # Backpropagation if predicted value is different from target value
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

        # Reset to root-position
        self.board.set_status("-")
        self.board.set_fen(root.get_fen())
        self.board.board_array = self.board.set_board_array()
        self.board.add_pieces()

        # Returning the chosen move and promoting
        print("\nChoosing move with prediction: {}\n".format(move_node.get_prediction()))
        return move_node.get_move()[0], move_node.get_move()[1], move_node.get_promote()

    def BFS(self, root, tic, seconds=5.0):
        """
        Breadth first search to get tree of positions
        :param root: (Node) root
        :param tic: (Float) Start-time of calling this function
        :param seconds: (Float) Time this function should take in seconds
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

            # Time that BFS should take to build the tree
            toc = time.time()
            if toc - tic > seconds:
                return

            # Get node-prediction for sorting on prediction
            fen = self.board.get_fen()
            data = util.get_data(fen)
            node_prediction, node_activation = self.perceptron.predict(data)

            # Flip prediction if current position has black to move
            if self.board.get_bw() == "b":
                node_prediction = 1.0 - node_prediction

            # Update depth for logging/printing
            new_full_move = self.board.get_full_move()
            new_depth = (new_full_move - full_move) * 2 + 1
            if color == "w" and self.board.get_bw() == "b":
                new_depth += 1
            elif color == "b" and self.board.get_bw() == "w":
                new_depth -= 1
            if new_depth != depth:
                depth = new_depth
                print("Depth: {}".format(depth))

            # List of moves in current position
            self.move_list = []
            moves = []

            # Go through every square of the board, find every possible move and move them to find prediction
            for row in range(8):
                for col in range(8):
                    fr = [row, col]

                    # Find legal moves
                    legal_moves = chess_logic.legal_moves(
                        self.board.get_board_array(),
                        fr,
                        self.board.get_bw(),
                        self.board.get_castle(),
                        self.board.get_en_passent()
                    )

                    for m in legal_moves:
                        to = [fr[0] + m[0], fr[1] + m[1]]
                        moves.append([fr, to])

            # Go through every move
            for m in moves:
                tic1 = time.time()

                fr = m[0]
                to = m[1]

                # Move piece
                self.board.move_piece(fr, to)

                # If move did that a pawn can promote
                if self.board.get_promoting():
                    for piece in ["q", "r", "b", "n"]:
                        self.board.set_fen(node.get_fen())
                        self.board.board_array = self.board.set_board_array()
                        self.board.add_pieces()

                        self.board.move_piece(fr, to)
                        self.board.promote_pawn(to, piece, print_promote=False)

                        br_out = self.predict_on_new_position_and_add_to_move_list(
                            fr,
                            to,
                            piece
                        )

                        if br_out:
                            break

                else:  # If ordinary move
                    br_out = self.predict_on_new_position_and_add_to_move_list(
                        fr,
                        to,
                        None
                    )

                self.board.set_fen(node.get_fen())
                self.board.board_array = self.board.set_board_array()
                self.board.add_pieces()

                toc1 = time.time()
                self.predict_time.append(toc1-tic1)

                if br_out:
                    break

            # Add moves and positions from move list to node_list and position-tree
            for m in self.move_list:
                fr = m[0][0]
                to = m[0][1]
                prediction = m[1]
                activations = m[2]
                fen = m[3]
                bw = m[4]
                promote_piece = m[5]

                # Make new Node for child
                child = position_nodes.Node(
                    prediction,
                    activations,
                    fen,
                    bw,
                    promote_piece,
                    ((node_prediction * 10) + (prediction - node_prediction))
                )
                # Add child to parent-node
                node.add_child(child, [fr, to], self.board.get_bw())
                # Add child to node_list
                node_list.append(child)

            # Sort node_list so it always checks the node with the greatest prediction next
            node_list.sort(key=sort_node_func, reverse=True)

    def minimax(self, position, alpha, beta, maximizing_player):
        """
        Minimax-algorithm with alpha-beta pruning
        :param position: Node-position
        :param alpha:
        :param beta:
        :param maximizing_player: (Boolean) True if white, False if black
        :return:
        """
        if position.get_bw() == "w":
            position.set_prediction(1.0 - position.get_prediction())

        if len(position.get_children()) == 0:
            return position

        ret_pos = position
        alpha2 = alpha
        beta2 = beta

        if maximizing_player:
            max_eval = -0.1
            position.get_children().sort(key=sort_children_func, reverse=True)
            for child in position.get_children():
                pos = self.minimax(child, alpha2, beta2, False)
                eval = pos.get_prediction()
                if eval >= max_eval:
                    max_eval = eval
                    ret_pos = child
                    ret_pos.set_prediction(eval)
                alpha2 = max(alpha2, eval)
                if beta2 <= alpha2:
                    break
        else:
            min_eval = 1.1
            position.get_children().sort(key=sort_children_func, reverse=True)
            for child in position.get_children():
                pos = self.minimax(child, alpha2, beta2, True)
                eval = pos.get_prediction()
                if eval <= min_eval:
                    min_eval = eval
                    ret_pos = child
                    ret_pos.set_prediction(eval)
                beta2 = min(beta2, eval)
                if beta2 <= alpha2:
                    break
        return ret_pos

    def predict_pos(self):
        """
        Get prediction, activation and fen from position
        :return: prediction, activations, fen
        """
        # Get fen and predict
        fen = self.board.get_fen()
        data = util.get_data(fen)
        prediction, activations = self.perceptron.predict(data)

        # Update prediction if game is finished
        if finished_game(self.board.get_status()):
            prediction = finished_prediction(self.board.get_status())

        # Flip prediction if white is to move next (meaning that black has the current move)
        if self.board.get_bw() == "w":
            prediction = 1.0 - prediction

        return prediction, activations, fen

    def predict_on_new_position_and_add_to_move_list(self, fr, to, piece):
        """
        Predicts on position after a move and adds info to list of moves
        :param fr: (List) Square to move from
        :param to: (List) Square to move to
        :param piece: (String) which piece we have promoted to. None if no piece has been promoted
        :return: move_list (updated list of moves), br_out (if we should break out of loop)
        """
        br_out = False
        self.board.next_turn(visual=True)

        # Prediction on position
        prediction, activations, fen = self.predict_pos()

        # Add move with prediction and other info to list of moves
        self.move_list.append([[fr, to], prediction, activations, fen, self.board.get_bw(), piece])

        # If move made that we win, we can't find any better move
        # So we can set "break out" to True
        if prediction == 1.0:
            br_out = True

        # Reset status and positions so far in game
        self.board.set_status("-")
        self.board.positions_in_game[self.board.get_fen_pos()] -= 1

        return br_out
