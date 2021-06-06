import json
import numpy as np
import random


EMPTY = 0
PAWN = 1
KNIGHT = 2
BISHOP = 3
ROOK = 4
QUEEN = 5
KING = 6
piece_dict = {"p": PAWN, "n": KNIGHT, "b": BISHOP, "r": ROOK, "q": QUEEN, "k": KING}


def add_piece_to_list(piece):
    piece_list = [0 for _ in range(12)]
    if piece.islower():
        piece_list[(piece_dict[piece.lower()] - 1) * 2] = 1
    elif piece.isupper():
        piece_list[(piece_dict[piece.lower()] * 2) - 1] = 1
    return piece_list


def fen_to_list(fen):
    """
    Makes fen-string to a list for use with perceptron
    :param fen: fen-string
    :return: a list
    """
    fen_list = fen.split()
    value_list = []
    # Board
    for c in fen_list[0]:
        if c.lower() in piece_dict:
            for p in add_piece_to_list(c):
                value_list.append(p)
        try:
            number = int(c)
            for _ in range(number):
                for _ in range(12):
                    value_list.append(0)
        except ValueError:
            pass
    # Black or White
    if fen_list[1] == "w":
        value_list.append(1)
    if fen_list[1] == "b":
        value_list.append(-1)

    # Castle
    castle_list = [0, 0, 0, 0]
    if "K" in fen_list[2]:
        castle_list[0] = 1
    if "Q" in fen_list[2]:
        castle_list[1] = 1
    if "k" in fen_list[2]:
        castle_list[2] = 1
    if "q" in fen_list[2]:
        castle_list[3] = 1
    for c in castle_list:
        value_list.append(c)

    # En passent
    number = string_pos_to_number(fen_list[3])
    en_passent = [0 for _ in range(16)]
    if int(number/8) == 2:
        en_passent[(number % 8) - 1] = 1
    elif int(number/8) == 5:
        en_passent[8 + (number % 8) - 1] = 1
    for p in en_passent:
        value_list.append(p)

    # Half-move
    try:
        value_list.append(int(fen_list[4]))
    except ValueError:
        value_list.append(0)

    # Full-move
    try:
        value_list.append(int(fen_list[5]))
    except ValueError:
        value_list.append(0)

    return value_list


def string_pos_to_number(pos):
    """
    Converts string-pos to number
    :param pos: Position as string
    :return: Position as number on board
    """
    if pos == "-":
        return 0
    col = 8-int(pos[1])
    row = 0
    num_string = [c for c in ["a", "b", "c", "d", "e", "f", "g", "h"]]
    for i in range(8):
        if pos[0] == num_string[i]:
            row = i
    return row + (col*8) + 1


def move_from_to(pos, move):
    """
    Returns a list with from-position and to-position
    :param pos: current position
    :param move: move from current position
    :return: [[from_x, from_y], [to_x, to_y]]
    """
    ret_list = [0 for _ in range(64)]
    for i in range(len(ret_list)):
        if int(i / 8) == pos[0] and i % 8 == pos[1]:
            ret_list[i] = -1
        elif int(i / 8) == pos[0]+move[0] and i % 8 == pos[1]+move[1]:
            ret_list[i] = 1
    return ret_list


def get_move_from_to(data):
    """
    Gets move from and to from dataset
    :param data: dataset
    :return: move_from, move_to
    """
    move_list = data[0][0][-64:]
    move_from = [9, 9]
    move_to = [9, 9]
    for i in range(len(move_list)):
        if move_list[i] == -1:
            move_from[0] = int(i/8)
            move_from[1] = i % 8
        if move_list[i] == 1:
            move_to[0] = int(i/8)
            move_to[1] = i % 8
    if move_from == [9, 9] or move_to == [9, 9]:
        raise Exception("Couldn't find moves")
    return move_from, move_to


def add_move_list_to_fen_list(fen_list, move_list):
    """
    Adds move to fen_list for perceptron
    :param fen_list: fen as a list
    :param move_list: move as a list on the form [[from_x, from_y], [to_x, to_y]]
    :return: a 1d-list with fen_list first and move_list last
    """
    ret_list = fen_list.copy()
    for move in move_list:
        ret_list.append(move)
    return ret_list


def get_data(fen):
    """
    Gets data for use with perceptron
    :param fen: fen-string from chess-game
    :return: a list for perceptron
    """
    return fen_to_list(fen)


def get_promote_data(fen, piece):
    """
    Gets data for promotion
    :param fen: fen-string
    :param piece: which piece to promote to. "n", "b", "r" or "q"
    :return: a list for promote-perceptron
    """
    ret_list = fen_to_list(fen)
    promote_list = [0 for _ in range(8)]
    if piece.lower() == "n":
        if piece.islower():
            promote_list[0] = 1
        else:
            promote_list[1] = 1
    elif piece.lower() == "b":
        if piece.islower():
            promote_list[2] = 1
        else:
            promote_list[3] = 1
    elif piece.lower() == "r":
        if piece.islower():
            promote_list[4] = 1
        else:
            promote_list[5] = 1
    elif piece.lower() == "q":
        if piece.islower():
            promote_list[6] = 1
        else:
            promote_list[7] = 1
    for p in promote_list:
        ret_list.append(p)
    return ret_list


def get_weights(file, layer_sizes=None):
    """
    Get weights from json-file. Makes new weights if file doesn't exist or is empty
    :param layer_sizes:
    :param file: json-file
    :return: list of weights
    """
    # For testing
    if layer_sizes is None:
        layer_sizes = np.array([6, 4, 1])

    depth = len(layer_sizes)
    try:
        weights = np.load(file, allow_pickle=True)
    except FileNotFoundError:
        new_weights = []
        for i in range(depth - 1):
            new_weights.append(np.random.randn(layer_sizes[i] + 1, layer_sizes[i+1]) * 0.1)
        new_weights = np.array(new_weights, dtype=object)
        np.save(file, new_weights)
        weights = np.load(file, allow_pickle=True)
    return weights


def save_weights(weights, file):
    """
    Save weights to file
    :param weights: weights to save
    :param file: file to save to. will make a new file if it doesn't exist
    :return:
    """
    np.save(file, weights)


def add_bias(data):
    ret_list = [-1]
    for d in data:
        ret_list.append(d)
    return ret_list


def roulette_wheel(predictions):
    """
    Using the roulette wheel algorithm to choose move
    :param predictions: list of moves
    :return:
    """
    total = 0
    for p in predictions:
        total += float(p[1])
    if total == 0.0:
        total = 1e-17
    prob_list = []
    total_prob = 0
    for i in range(len(predictions)):
        prob_list.append(float((predictions[i][1]) / total) + total_prob)
        total_prob += float(predictions[i][1]) / total
    r = random.random()
    i = 0
    try:
        while prob_list[i] < r:
            i += 1
    except IndexError:
        i = len(prob_list)-1
    if i > len(prob_list)-1:
        i = len(prob_list)-1
    return predictions[i]


def decide_from_predictions(predictions):
    """
    Returns the best move, or using the roulette-wheel to get best move
    if the two best moves is closer than 0.005 in prediction
    :param predictions: list of moves
    :return:
    """
    if len(predictions) == 0:
        raise Exception("No predictions to decide from!!!!!!")
    # Return if only one prediction
    if len(predictions) == 1:
        print("Only one possible move")
        return predictions[0]

    # Get the best two moves
    best_moves = []
    for p in predictions:
        if len(best_moves) == 0:
            best_moves.append(p)
        elif len(best_moves) == 1:
            if p[1] > best_moves[0][1]:
                temp = best_moves.pop()
                best_moves.append(p)
                best_moves.append(temp)
            else:
                best_moves.append(p)
        elif len(best_moves) == 2:
            if p[1] > best_moves[0][1]:
                temp = best_moves[0]
                best_moves[0] = p
                best_moves[1] = temp
            elif p[1] > best_moves[1][1]:
                best_moves[1] = p

    # If similar (less than 0.005 in prediction apart), do roulette-wheel
    if abs(best_moves[0][1] - best_moves[1][1]) < 0.005:
        print("Using roulette-wheel to get move")
        return roulette_wheel(predictions)
    print("Choosing best move")
    return best_moves[0]


def update_game_log(result):
    try:
        with open("data/result.json", "r") as f:
            try:
                result_dict = json.load(f)
            except json.JSONDecodeError:
                result_dict = {"Games played": 0, "White wins": 0, "Black Wins": 0, "Draw": 0}
    except FileNotFoundError:
        # File not found, make file and adding result
        result_dict = {"Games played": 0, "White wins": 0, "Black Wins": 0, "Draw": 0}
    result_dict["Games played"] += 1
    if result == "w":
        result_dict["White wins"] += 1
    if result == "b":
        result_dict["Black Wins"] += 1
    if result == "d":
        result_dict["Draw"] += 1
    j = json.dumps(result_dict)
    with open("data/result.json", "w") as f:
        f.write(j)

