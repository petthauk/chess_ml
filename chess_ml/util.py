import numpy as np
import pandas
import random


EMPTY = 0
PAWN = 1
KNIGHT = 2
BISHOP = 3
ROOK = 4
QUEEN = 5
KING = 6


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
        if c == "p":
            value_list.append(PAWN*-1)
        if c == "n":
            value_list.append(KNIGHT*-1)
        if c == "b":
            value_list.append(BISHOP*-1)
        if c == "r":
            value_list.append(ROOK*-1)
        if c == "q":
            value_list.append(QUEEN*-1)
        if c == "k":
            value_list.append(KING*-1)
        if c == "P":
            value_list.append(PAWN)
        if c == "N":
            value_list.append(KNIGHT)
        if c == "B":
            value_list.append(BISHOP)
        if c == "R":
            value_list.append(ROOK)
        if c == "Q":
            value_list.append(QUEEN)
        if c == "K":
            value_list.append(KING)
        try:
            number = int(c)
            for _ in range(number):
                value_list.append(EMPTY)
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
    value_list.append(string_pos_to_number(fen_list[3]))

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
    :return: a list on the form [[from_x, from_y], [to_x, to_y]]
    """
    return [[pos[0], pos[1]], [pos[0]+move[0], pos[1]+move[1]]]


def add_move_list_to_fen_list(fen_list, move_list):
    """
    Adds move to fen_list for perceptron
    :param fen_list: fen as a list
    :param move_list: move as a list on the form [[from_x, from_y], [to_x, to_y]]
    :return: a 1d-list with fen_list first and move_list last
    """
    ret_list = fen_list.copy()
    for move in move_list:
        for elem in move:
            ret_list.append(elem)
    return ret_list


def get_data(fen, square, move):
    """
    Gets data for use with perceptron
    :param fen: fen-string from chess-game
    :param square: which square we are checking move from
    :param move: current move to check
    :return: a list for perceptron
    """
    return add_move_list_to_fen_list(fen_to_list(fen), move_from_to(square, move))


def get_promote_data(fen, piece):
    """
    Gets data for promotion
    :param fen: fen-string
    :param piece: which piece to promote to. "n", "b", "r" or "q"
    :return: a list for promote-perceptron
    """
    ret_list = fen_to_list(fen)
    if piece == "n":
        ret_list.append(KNIGHT)
    if piece == "b":
        ret_list.append(BISHOP)
    if piece == "r":
        ret_list.append(ROOK)
    if piece == "q":
        ret_list.append(QUEEN)
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


def decide_from_predictions(predictions):
    total = 0
    for p in predictions:
        total += p[1]
    prob_list = []
    total_prob = 0
    for i in range(len(predictions)):
        prob_list.append((predictions[i][1] / total) + total_prob)
        total_prob += predictions[i][1] / total
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
