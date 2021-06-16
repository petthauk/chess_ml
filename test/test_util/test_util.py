import random
import os
import pytest
import numpy as np
import util.util as util

fen = "rn1qkbnr/pp2pppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 50 124"
piece_list = ["p", "n", "b", "r", "q", "k", "P", "N", "B", "R", "Q", "K"]
fen_list = [
        0, 0, 0, -1, 0, 0,
        0, -1, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, -1, 0,
        0, 0, 0, 0, 0, -1,
        0, 0, -1, 0, 0, 0,
        0, -1, 0, 0, 0, 0,
        0, 0, 0, -1, 0, 0,

        -1, 0, 0, 0, 0, 0,
        -1, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,
        -1, 0, 0, 0, 0, 0,
        -1, 0, 0, 0, 0, 0,
        -1, 0, 0, 0, 0, 0,
        -1, 0, 0, 0, 0, 0,

        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,

        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,

        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,

        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0,

        1, 0, 0, 0, 0, 0,
        1, 0, 0, 0, 0, 0,
        1, 0, 0, 0, 0, 0,
        1, 0, 0, 0, 0, 0,
        1, 0, 0, 0, 0, 0,
        1, 0, 0, 0, 0, 0,
        1, 0, 0, 0, 0, 0,
        1, 0, 0, 0, 0, 0,

        0, 0, 0, 1, 0, 0,
        0, 1, 0, 0, 0, 0,
        0, 0, 1, 0, 0, 0,
        0, 0, 0, 0, 1, 0,
        0, 0, 0, 0, 0, 1,
        0, 0, 1, 0, 0, 0,
        0, 1, 0, 0, 0, 0,
        0, 0, 0, 1, 0, 0,

        1,
        1, 1, 1, 1,
        0, 0, 0, 0, 0, 0, 0, 0,
        50,
        124
    ]
sample_data = [[[2, 3, 4, 5, 6, 7], [1]], 0.34]

letter_pos = ["a", "b", "c", "d", "e", "f", "g", "h"]
number_pos = [str(i) for i in range(8, 0, -1)]
all_string_pos = []
for number in number_pos:
    for letter in letter_pos:
        all_string_pos.append(letter + number)


def test_add_piece_to_list_black_pawn():
    assert util.add_piece_to_list("p") == [-1, 0, 0, 0, 0, 0]


def test_add_piece_to_list_white_pawn():
    assert util.add_piece_to_list("P") == [1, 0, 0, 0, 0, 0]


def test_add_piece_to_list_black_knight():
    assert util.add_piece_to_list("n") == [0, -1, 0, 0, 0, 0]


def test_add_piece_to_list_white_knight():
    assert util.add_piece_to_list("N") == [0, 1, 0, 0, 0, 0]


def test_add_piece_to_list_black_bishop():
    assert util.add_piece_to_list("b") == [0, 0, -1, 0, 0, 0]


def test_add_piece_to_list_white_bishop():
    assert util.add_piece_to_list("B") == [0, 0, 1, 0, 0, 0]


def test_add_piece_to_list_black_rook():
    assert util.add_piece_to_list("r") == [0, 0, 0, -1, 0, 0]


def test_add_piece_to_list_white_rook():
    assert util.add_piece_to_list("R") == [0, 0, 0, 1, 0, 0]


def test_add_piece_to_list_black_queen():
    assert util.add_piece_to_list("q") == [0, 0, 0, 0, -1, 0]


def test_add_piece_to_list_white_queen():
    assert util.add_piece_to_list("Q") == [0, 0, 0, 0, 1, 0]


def test_add_piece_to_list_black_king():
    assert util.add_piece_to_list("k") == [0, 0, 0, 0, 0, -1]


def test_add_piece_to_list_white_king():
    assert util.add_piece_to_list("K") == [0, 0, 0, 0, 0, 1]


def test_fen_to_list():
    ret_list = util.fen_to_list(fen)
    x = 0
    for i in range(len(fen_list)):
        if x % (6*8) == 0:
            print("New Line")
        if x % 6 == 0:
            print("Next square")
        x += 1
        print("{} {}".format(fen_list[i], ret_list[i]))
        try:
            assert fen_list[i] == ret_list[i]
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


def test_get_move_from_to_return_to():
    _, to = util.get_move_from_to(sample_data)
    assert to == [6, 7]


def test_get_move_from_to_return_from():
    fr, _ = util.get_move_from_to(sample_data)
    assert fr == [4, 5]


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
    f_list = [random.randint(0, 7), random.randint(0, 7)]
    ret_list = [
        f_list[0],
        f_list[1],
        move_list[0][0],
        move_list[0][1],
        move_list[1][0],
        move_list[1][1]
    ]
    assert util.add_move_list_to_fen_list(f_list, move_list) == ret_list


def test_get_data():
    answer_list = fen_list.copy()
    square = [1, 2]
    move = [3, 4]
    for s in square:
        answer_list.append(s)
    for m in range(len(move)):
        answer_list.append(square[m]+move[m])
    ret_list = util.get_data(fen, square, move)
    print(ret_list)
    for i in range(len(answer_list)):
        assert ret_list[i] == answer_list[i]


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


def test_string_position_to_array_position():
    array_row = 0
    array_col = 0
    for pos in all_string_pos:
        assert util.string_position_to_array_position(pos) == [array_row, array_col]
        array_col += 1
        if array_col == 8:
            array_col = 0
            array_row += 1


def test_array_position_to_string_position():
    array_row = 0
    array_col = 0
    for pos in all_string_pos:
        assert util.array_position_to_string_position([array_row, array_col]) == pos
        array_col += 1
        if array_col == 8:
            array_col = 0
            array_row += 1

