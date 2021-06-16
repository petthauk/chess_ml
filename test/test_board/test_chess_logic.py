import board.chess_logic as cl
from board import chess_board
import unittest

board = chess_board.Board(fen="8/8/8/8/8/8/8/8 w KQkq - 0 0")


def legal_move_help(t, right_move):
    """
    Helper function for test_legal_move
    :param t: Type of piece
    :param right_move: The right moves for the piece
    :return:
    """
    board.get_board_array()[4, 4].add_content(piece=board.Piece(t))
    move = []
    if t.islower():
        move = cl.legal_moves(board.get_board_array(), (4, 4), "b")
    elif t.isupper():
        move = cl.legal_moves(board.get_board_array(), (4, 4), "w")
    board.get_board_array()[4, 4].add_content()
    for r in right_move:
        assert r in move
        move.remove(r)
    assert len(move) == 0


def test_add_move_for_straight_line_pieces():
    move = cl.add_move_for_straight_line_pieces(
        [
            [-1, 0],
            [0, -1],
            [1, 0],
            [0, 1]
        ],
        4,
        4,
        board.get_board_array(),
        board.Piece("r"),
        []
    )
    right_moves = [
        [-1, 0],
        [-2, 0],
        [-3, 0],
        [-4, 0],
        [0, -1],
        [0, -2],
        [0, -3],
        [0, -4],
        [0, 1],
        [0, 2],
        [0, 3],
        [1, 0],
        [2, 0],
        [3, 0]
    ]
    for r in right_moves:
        assert r in move


def test_legal_moves_for_white_pawn():
    legal_move_help("P", [[-1, 0]])


def test_legal_moves_for_black_pawn():
    legal_move_help("p", [[1, 0]])


def test_legal_moves_for_rook():
    legal_move_help(
        "r",
        [
            [-1, 0],
            [-2, 0],
            [-3, 0],
            [-4, 0],
            [1, 0],
            [2, 0],
            [3, 0],
            [0, -1],
            [0, -2],
            [0, -3],
            [0, -4],
            [0, 1],
            [0, 2],
            [0, 3]
        ]
    )


def test_legal_moves_for_knight():
    legal_move_help(
        "n",
        [
            [-2, -1],
            [-2, 1],
            [-1, -2],
            [-1, 2],
            [1, -2],
            [1, 2],
            [2, -1],
            [2, 1]
        ]
    )


def test_legal_moves_for_bishop():
    legal_move_help(
        "b",
        [
            [-1, -1],
            [-2, -2],
            [-3, -3],
            [-4, -4],
            [-1, 1],
            [-2, 2],
            [-3, 3],
            [1, -1],
            [2, -2],
            [3, -3],
            [1, 1],
            [2, 2],
            [3, 3]
        ]
    )


def test_legal_moves_for_queen():
    legal_move_help(
        "q",
        [
            [-1, -1],
            [-2, -2],
            [-3, -3],
            [-4, -4],
            [-1, 0],
            [-2, 0],
            [-3, 0],
            [-4, 0],
            [-1, 1],
            [-2, 2],
            [-3, 3],
            [0, 1],
            [0, 2],
            [0, 3],
            [1, 1],
            [2, 2],
            [3, 3],
            [1, 0],
            [2, 0],
            [3, 0],
            [1, -1],
            [2, -2],
            [3, -3],
            [0, -1],
            [0, -2],
            [0, -3],
            [0, -4]
        ]
    )


def test_legal_moves_for_king():
    legal_move_help(
        "k",
        [
            [-1, -1],
            [-1, 0],
            [-1, 1],
            [0, -1],
            [0, 1],
            [1, -1],
            [1, 0],
            [1, 1]
        ]
    )


def test_check_false():
    unittest.TestCase.assertFalse(
        unittest.TestCase(),
        cl.check(board.get_board_array(), board.get_bw())
    )


def test_check_true_white_to_move():
    board.get_board_array()[2, 2].add_content(board.Piece("K"))
    board.get_board_array()[3, 3].add_content(board.Piece("q"))
    assert cl.check(board.get_board_array(), "w")
    board.get_board_array()[2, 2].add_content()
    board.get_board_array()[3, 3].add_content()


def test_check_true_black_to_move():
    board.get_board_array()[2, 2].add_content(board.Piece("k"))
    board.get_board_array()[3, 3].add_content(board.Piece("Q"))
    assert cl.check(board.get_board_array(), "b")
    board.get_board_array()[2, 2].add_content()
    board.get_board_array()[3, 3].add_content()


def test_check_with_same_color_on_pieces():
    board.get_board_array()[2, 2].add_content(board.Piece("k"))
    board.get_board_array()[3, 3].add_content(board.Piece("q"))
    unittest.TestCase.assertFalse(
        unittest.TestCase(),
        cl.check(board.get_board_array(), "w")
    )


def test_add_en_passant_adds_move():
    moves = cl.add_en_passant([3, 3], [], "e6")
    assert [-1, 1] in moves


def test_add_en_passant_no_moves_added():
    moves = []
    moves_after = cl.add_en_passant([3, 3], moves, "f7")
    assert moves == moves_after


def test_add_en_passant_without_en_passant():
    moves = []
    moves_after = cl.add_en_passant([3, 3], moves, "-")
    assert moves == moves_after
