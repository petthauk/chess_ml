import chess_ml.util as util
import pytest

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
