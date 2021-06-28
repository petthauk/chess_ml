import util.util as util


def add_move_for_straight_line_pieces(move_matrix, row, col, game_board, piece, moves):
    """
    Adds moves for Rook, Bishop and Queen
    :param move_matrix: How the piece moves. Will continue in a straight line in these directions.
    :param row: Which row the piece is on
    :param col: Which column the piece is on
    :param game_board: game_board array
    :param piece: The piece
    :param moves: Current moves
    :return: Array of legal moves
    """
    for m in move_matrix:
        for i in range(1, 8):
            target_row = row + (i * m[0])
            target_col = col + (i * m[1])
            if 0 <= target_row < 8 and 0 <= target_col < 8:
                target = game_board[target_row, target_col].get_content()
                if target is not None:
                    if (
                            piece.get_type().islower() and target.get_type().isupper()
                    ) or (
                            piece.get_type().isupper() and target.get_type().islower()
                    ):
                        moves.append([i * m[0], i * m[1]])
                    break
                moves.append([i * m[0], i * m[1]])
            else:
                break
    return moves


def legal_moves(game_board, position, bw, castle="KQkq", en_passant="-", rec=True):
    """
    Returns a list of legal moved based on position on board
    :param en_passant: String to tell if en passant or not
    :param castle: String that contains info of castling-rights
    :param rec: Recursion for check
    :param game_board: 2d-array of game-board
    :param position: list with position to check legal moves from
    :param bw: Black or White to move (for check-checking)
    :return: List of legal moves, None if no piece on position
    """
    row = position[0]
    col = position[1]
    # List of moves
    moves = []
    # Piece on position
    piece = game_board[row, col].get_content()
    # If no piece on position
    if piece is None:
        return moves
    # If wrong color
    if (piece.get_type().islower() and bw == "w") or (piece.get_type().isupper() and bw == "b"):
        return moves

    # White Pawn
    if piece.get_type() == "P":
        if row > 0:
            if game_board[row - 1, col].get_content() is None:
                moves.append([-1, 0])
                if row == 6 and game_board[row - 2, col].get_content() is None:
                    moves.append([-2, 0])
            if col != 0:
                if game_board[row - 1, col - 1].get_content() is not None:
                    if game_board[row - 1, col - 1].get_content().get_type().islower():
                        moves.append([-1, -1])
            if col != 7:
                if game_board[row - 1, col + 1].get_content() is not None:
                    if game_board[row - 1, col + 1].get_content().get_type().islower():
                        moves.append([-1, +1])
        else:  # Will be promoted
            for p in ["Q", "R", "N", "B"]:
                game_board[row, col].get_content().set_type(p)
                for m in legal_moves(game_board, position, bw, castle, en_passant, rec):
                    moves.append(m)
            # Change back to pawn
            game_board[row, col].get_content().set_type("P")
        moves = add_en_passant(position, moves, en_passant)

    # Black Pawn
    elif piece.get_type() == "p":
        if row < 7:
            if game_board[row + 1, col].get_content() is None:
                moves.append([1, 0])
                if row == 1 and game_board[row + 2, col].get_content() is None:
                    moves.append([2, 0])
            if col != 0:
                if game_board[row + 1, col - 1].get_content() is not None:
                    if game_board[row + 1, col - 1].get_content().get_type().isupper():
                        moves.append([1, -1])
            if col != 7:
                if game_board[row + 1, col + 1].get_content() is not None:
                    if game_board[row + 1, col + 1].get_content().get_type().isupper():
                        moves.append([1, 1])
        else:  # Will be promoted
            for p in ["q", "r", "n", "b"]:
                game_board[row, col].get_content().set_type(p)
                for m in legal_moves(game_board, position, bw, castle, en_passant, rec):
                    moves.append(m)
            # Change back to pawn
            game_board[row, col].get_content().set_type("p")

        moves = add_en_passant(position, moves, en_passant)

    # Rook
    elif piece.get_type().lower() == "r":
        move_matrix = [
            [-1, 0],
            [0, -1],
            [1, 0],
            [0, 1]
        ]
        moves = add_move_for_straight_line_pieces(
            move_matrix,
            row,
            col,
            game_board,
            piece,
            moves
        )

    # Knight
    elif piece.get_type().lower() == "n":
        move_list = [-2, -1, 1, 2]
        for add_row in move_list:
            for add_col in move_list:
                if abs(add_row) != abs(add_col):
                    if 0 <= row + add_row < 8:
                        if 0 <= col + add_col < 8:
                            if game_board[row + add_row, col + add_col].get_content() is not None:
                                if piece.get_type().islower():
                                    if game_board[row + add_row, col + add_col].get_content().get_type().isupper():
                                        moves.append([add_row, add_col])
                                if piece.get_type().isupper():
                                    if game_board[row + add_row, col + add_col].get_content().get_type().islower():
                                        moves.append([add_row, add_col])
                            else:
                                moves.append([add_row, add_col])

    # Bishop
    elif piece.get_type().lower() == "b":
        move_matrix = [
            [-1, -1],
            [-1, 1],
            [1, -1],
            [1, 1]
        ]
        moves = add_move_for_straight_line_pieces(
            move_matrix,
            row,
            col,
            game_board,
            piece,
            moves
        )

    # Queen
    elif piece.get_type().lower() == "q":
        move_matrix = [
            [-1, -1],
            [-1, 0],
            [-1, 1],
            [0, -1],
            [0, 1],
            [1, -1],
            [1, 0],
            [1, 1]
        ]
        moves = add_move_for_straight_line_pieces(
            move_matrix,
            row,
            col,
            game_board,
            piece,
            moves
        )

    # King
    elif piece.get_type().lower() == "k":
        king_moves = [
            [-1, -1],
            [-1, 0],
            [-1, 1],
            [0, -1],
            [0, 1],
            [1, -1],
            [1, 0],
            [1, 1]
        ]
        for m in king_moves:
            if 0 <= row + m[0] < 8 and 0 <= col + m[1] < 8:
                target = game_board[row + m[0], col + m[1]].get_content()
                if target is not None:
                    if (
                            piece.get_type().islower() and target.get_type().isupper()
                    ) or (
                            piece.get_type().isupper() and target.get_type().islower()
                    ):
                        moves.append(m)
                else:
                    moves.append(m)
        if (rec and (
                piece.get_type().islower() and position == [0, 4]
                or
                piece.get_type().isupper() and position == [7, 4])):
            moves = castling(game_board, castle, moves, piece.get_type())

    # Cannot move into check
    moves = delete_discovered_check(moves, position, game_board, bw, rec)

    return moves


def delete_discovered_check(moves, position, game_board, bw, rec):
    """
    Move piece to check if it discovers check
    :param rec: Recursion, decides if we should go deeper or not
    :param moves: list of moves
    :param position: position of piece
    :param game_board: board-array
    :param bw: Black or White to move
    :return: List of new moves
    """
    new_m = moves.copy()
    # Try to move piece to see if it resolves the check
    for m in moves:
        target_square = []

        for j in range(len(m)):
            target_square.append(
                position[j] + m[j]
            )
        # Move piece
        target_piece = game_board[target_square[0], target_square[1]].get_content()
        game_board[target_square[0], target_square[1]].add_content(
            game_board[position[0], position[1]].get_content()
        )
        game_board[position[0], position[1]].add_content()

        # Check for check and delete move if still check
        if check(game_board, bw, rec):
            new_m.remove(m)

        # Move piece back
        game_board[position[0], position[1]].add_content(
            game_board[target_square[0], target_square[1]].get_content()
        )
        game_board[target_square[0], target_square[1]].add_content(target_piece)
    return new_m


def find_king(game_board, bw):
    """
    Finds right king
    :param game_board: array of board
    :param bw: black or white to move?
    :return: Square with king, None if king isn't present
    """
    # Find king
    for r in game_board:
        for sqr in r:
            if sqr.get_content() is not None:
                if sqr.get_content().get_type() == "K" and bw == "w":
                    return sqr
                elif sqr.get_content().get_type() == "k" and bw == "b":
                    return sqr
    # Didn't find king. Will hopefully never reach this
    return None


def check(game_board, bw, recursion=True):
    """
    Checks if it is check
    :param game_board: Array of board
    :param bw: Black or White to move
    :param recursion: Used to not check check when one move ahead
    :return: True if it is check, False otherwise
    """
    king_square = find_king(game_board, bw)
    if king_square is not None and recursion:
        for row in game_board:
            for sqr in row:
                if sqr.get_content() is not None:
                    if (
                            sqr.get_content().get_type().islower() and bw == "w"
                    ) or (
                            sqr.get_content().get_type().isupper() and bw == "b"
                    ):
                        moves = legal_moves(game_board, sqr.get_position(), "-", rec=False)
                        for m in moves:
                            target_pos = []
                            for i in range(len(m)):
                                target_pos.append(
                                    sqr.get_position()[i] + m[i]
                                )
                            if target_pos == king_square.get_position():
                                return True
    return False


def castling(game_board, castle, move, piece):
    """
    Checks if we can castle and add move if we can
    :param game_board: array of board
    :param castle: castle-string
    :param move: list of moves
    :param piece: piece to move (King)
    :return: updated list of moves
    """
    m = move
    if piece.isupper():
        if "K" in castle:
            if (
                    game_board[7, 5].get_content() is None
                    and
                    game_board[7, 6].get_content() is None
            ):
                if (
                        move_and_check_for_check(game_board, [7, 4], [7, 5], "w")
                        and
                        move_and_check_for_check(game_board, [7, 4], [7, 6], "w")
                ):
                    m.append([0, 2])
        if "Q" in castle:
            if (
                    game_board[7, 3].get_content() is None
                    and
                    game_board[7, 2].get_content() is None
                    and
                    game_board[7, 1].get_content() is None
            ):
                if (
                        move_and_check_for_check(game_board, [7, 4], [7, 3], "w")
                        and
                        move_and_check_for_check(game_board, [7, 4], [7, 2], "w")
                        and
                        move_and_check_for_check(game_board, [7, 4], [7, 1], "w")
                ):
                    m.append([0, -2])
    if piece.islower():
        if "k" in castle:
            if (
                    game_board[0, 5].get_content() is None
                    and
                    game_board[0, 6].get_content() is None
            ):
                if (
                        move_and_check_for_check(game_board, [0, 4], [0, 5], "b")
                        and
                        move_and_check_for_check(game_board, [0, 4], [0, 6], "b")
                ):
                    m.append([0, 2])
        if "q" in castle:
            if (
                    game_board[0, 3].get_content() is None
                    and
                    game_board[0, 2].get_content() is None
                    and
                    game_board[0, 1].get_content() is None
            ):
                if (
                        move_and_check_for_check(game_board, [0, 4], [0, 3], "b")
                        and
                        move_and_check_for_check(game_board, [0, 4], [0, 2], "b")
                        and
                        move_and_check_for_check(game_board, [0, 4], [0, 1], "b")
                ):
                    m.append([0, -2])
    return m


def move_and_check_for_check(game_board, king_place, new_place, bw):
    """
    Helper-function for castling.
    Checks that king is not moving into attacked square
    :param game_board: The board
    :param king_place: Where is the king?
    :param new_place: Where we move to
    :param bw: Black or White to move?
    :return:
    """
    valid_move = True
    # Move King
    game_board[new_place[0], new_place[1]].add_content(
        game_board[king_place[0], king_place[1]].get_content()
    )
    game_board[king_place[0], king_place[1]].add_content()
    # Check for check
    if check(game_board, bw):
        valid_move = False
    # Move King Back
    game_board[king_place[0], king_place[1]].add_content(
        game_board[new_place[0], new_place[1]].get_content()
    )
    game_board[new_place[0], new_place[1]].add_content()
    return valid_move


def add_en_passant(position, moves, en_passant):
    """
    Add move for en passant
    :param position: Position of piece that will capture
    :param moves: Current moves of piece
    :param en_passant: Position for en passant
    :return: Updated moves with en passant
    """
    moves_2 = moves.copy()

    if en_passant != "-":
        # Check if white or black should make en passant
        wb = 0
        if position[0] == 3:    # White
            wb = -1
        elif position[0] == 4:  # Black
            wb = 1

        if wb != 0:
            # Transform en_passant String to position in game_board
            en_passant_pos = util.string_position_to_array_position(en_passant)

            move_left_right = [-1, 1]
            for m in move_left_right:
                target_pos = [position[0]+wb, position[1]+m]
                if en_passant_pos == target_pos:
                    move = [wb, m]
                    if move not in moves_2:
                        moves_2.append(move)

    return moves_2
