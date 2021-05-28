import random
import os

import pytest
import numpy as np

import chess_ml.util as util

fen = "rn1qkbnr/pp2pppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0"


def test_fen_to_list():
    answer_list = [
        -4, -2, 0, -5, -6, -3, -2, -4,
        -1, -1, 0, 0, -1, -1, -1, -1,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0,
        1, 1, 1, 1, 1, 1, 1, 1,
        4, 2, 3, 5, 6, 3, 2, 4,
        1,
        1,
        1,
        1,
        1,
        0,
        0,
        0
    ]
    ret_list = util.fen_to_list(fen)
    for i in range(len(answer_list)):
        print("{} {}".format(answer_list[i], ret_list[i]))
        try:
            assert answer_list[i] == ret_list[i]
        except AssertionError as e:
            pytest.fail(str(e)+" at position "+str(i))


def test_string_pos_to_number():
    string_list = [
        [
            b+str(a) for b in ["a", "b", "c", "d", "e", "f", "g", "h"]
        ] for a in range(8, 0, -1)
    ]
    string_list2 = []
    for r in string_list:
        for c in r:
            string_list2.append(c)
    for i in range(len(string_list2)):
        assert util.string_pos_to_number(string_list2[i]) == i+1


def test_move_from_to():
    pos = [random.randint(1, 7), random.randint(0, 4)]
    move = [-1, 3]
    assert util.move_from_to(pos, move) == [
        [pos[0], pos[1]],
        [pos[0]+move[0], pos[1]+move[1]]
    ]


def test_add_move_list_to_fen_list():
    move_list = [
        [
            random.randint(0, 7),
            random.randint(0, 7)
        ],
        [
            random.randint(0, 7),
            random.randint(0, 7)
        ]
    ]
    fen_list = [random.randint(0, 7), random.randint(0, 7)]
    ret_list = [
        fen_list[0],
        fen_list[1],
        move_list[0][0],
        move_list[0][1],
        move_list[1][0],
        move_list[1][1]
    ]
    assert util.add_move_list_to_fen_list(fen_list, move_list) == ret_list


def test_get_weights():
    ret_list = np.array(
        [
            np.array([0.1, 0.3, 0.2], dtype=object),
            np.array([1.2, 0.4], dtype=object)
        ], dtype=object)
    np.save("data/test_weights.npy", ret_list)
    w = util.get_weights("data/test_weights.npy")
    for i in range(len(ret_list)):
        for j in range(len(ret_list[i])):
            assert w[i][j] == ret_list[i][j]


def test_get_weights_no_file():
    if os.path.exists("data/test_weights.npy"):
        os.remove("data/test_weights.npy")
    w = util.get_weights("data/test_weights.npy")
    assert w.shape == (2, )
    assert w[0].shape == (7, 4)
    assert w[1].shape == (5, 1)


def test_save_weights():
    weights = np.array([4, 3])
    util.save_weights(weights, "data/test_weights.npy")
    w = util.get_weights("data/test_weights.npy")
    for i in range(len(weights)):
        assert weights[i] == w[i]


def test_add_bias():
    assert util.add_bias([2, 3]) == [-1, 2, 3]
    assert util.add_bias([4, 3, 2]) == [-1, 4, 3, 2]
