import board.chess_board as cb
import pytest

board = cb.Board()
square = board.Square(6, 3)


def test_set_name():
    assert square.set_name() == "d2"


def test_get_name():
    assert square.get_name() == "d2"


def test_set_and_get_board_array():
    square.set_board_array(board.get_board_array())
    for i in range(len(board.get_board_array())):
        for j in range(len(board.get_board_array()[i])):
            assert square.get_board()[i, j] == board.get_board_array()[i, j]


def test_remove_from_castle():
    board.castle = "KQkq"
    board.remove_from_castle("Q")
    assert board.get_castle() == "Kkq"


def test_get_status():
    assert board.get_status() == "-"


def test_set_status_valid():
    board.set_status("w")
    assert board.get_status() == "w"


def test_set_status_invalid():
    try:
        board.set_status("a")
        pytest.fail("board.set_status with parameter \"a\" should raise exception")
    except ValueError:
        pass
