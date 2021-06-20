import pygame as pg
from pygame.locals import *
import sys
import numpy as np
import os
import board.chess_logic as logic
import util.util as util

# Colors for square on board
WHITE_SQUARE = (255, 220, 177)
BLACK_SQUARE = (199, 122, 88)
CLICKED_SQUARE = (255, 0, 0)
HIGHLIGHT_WHITE_SQUARE = (255, 99, 71)
HIGHLIGHT_BLACK_SQUARE = (255, 60, 40)


def set_visual_piece(t):
    """
    Sets images for pieces
    :param t: type of piece
    :return: image of piece in pygame
    """
    img = None
    if t == "P":  # White Pawn
        img = pg.image.load(os.path.join("piece_img", "wP.png"))
    elif t == "N":  # White Knight
        img = pg.image.load(os.path.join("piece_img", "wN.png"))
    elif t == "B":  # White Bishop
        img = pg.image.load(os.path.join("piece_img", "wB.png"))
    elif t == "R":  # White Rook
        img = pg.image.load(os.path.join("piece_img", "wR.png"))
    elif t == "Q":  # White Queen
        img = pg.image.load(os.path.join("piece_img", "wQ.png"))
    elif t == "K":  # White King
        img = pg.image.load(os.path.join("piece_img", "wK.png"))
    elif t == "p":  # Black Pawn
        img = pg.image.load(os.path.join("piece_img", "bP.png"))
    elif t == "n":  # Black Knight
        img = pg.image.load(os.path.join("piece_img", "bN.png"))
    elif t == "b":  # Black Bishop
        img = pg.image.load(os.path.join("piece_img", "bB.png"))
    elif t == "r":  # Black Rook
        img = pg.image.load(os.path.join("piece_img", "bR.png"))
    elif t == "q":  # Black Queen
        img = pg.image.load(os.path.join("piece_img", "bQ.png"))
    elif t == "k":  # Black King
        img = pg.image.load(os.path.join("piece_img", "bK.png"))
    return img


class Board:
    """
    Chess-board class
    """
    def __init__(
            self,
            w=60 * 8,
            h=60 * 8,
            fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0"
    ):
        # Init data
        self.w = w
        self.h = h
        self.fen = fen
        self.fen_pos = ""
        self.bw = ""
        self.castle = ""
        self.en_passent = ""
        self.set_fen(self.fen)
        self.board_array = self.set_board_array()
        self.status = "-"
        self.half_move = 0
        self.full_move = 0
        self.positions_in_game = {self.fen_pos: 1}
        self.promoting = False

        # Init Pygame
        pg.init()
        self.font = pg.font.SysFont("Helvetica", 50)
        pg.display.set_caption("Chess")
        self.screen = pg.display.set_mode((self.w, self.h))
        self.update_board()

    def __str__(self):
        ret_string = ""
        for row in self.board_array:
            for col in row:
                ret_string += col.__str__() + " "
            ret_string += "\n"
        return ret_string

    def set_status(self, status):
        """
        Sets status of game. Default is "-"
        :param status: "w" if white wins, "b" if black wins, "d" if draw
        :return:
        """
        if status in ["w", "b", "d"]:
            self.status = status
        else:
            raise ValueError("Status of game can only be \"w\", \"b\" or \"d\", you tried to set status "+status)

    def get_status(self):
        """
        Gets status of game
        :return: "-" if game continues, "w" if white has won, "b" if black has won, "d" if draw
        """
        return self.status

    def set_fen(self, fen):
        """
        Set new fen
        :param fen: fen-string
        :return:
        """
        self.fen = fen
        fen_list = self.fen.split(" ")
        self.fen_pos = fen_list[0]
        self.bw = fen_list[1]
        self.castle = fen_list[2]
        self.en_passent = fen_list[3]
        try:
            self.half_move = int(fen_list[4])
            self.full_move = int(fen_list[5])
        except ValueError as e:
            print(e)

    def get_fen(self):
        """
        Returns fen as string
        :return: fen
        """
        return self.fen

    def get_fen_pos(self):
        """
        Returns fen as string
        :return: fen_string
        """
        return self.fen_pos

    def new_fen(self):
        """
        Make new fen based on board
        :return:
        """
        new_fen = ""
        row_num = 0
        for row in self.board_array:
            empty = 0
            for sq in row:
                if sq.get_content() is None:
                    empty += 1
                else:
                    if empty > 0:
                        new_fen += str(empty)
                    new_fen += sq.get_content().get_type()
                    empty = 0
            if empty > 0:
                new_fen += str(empty)
            if row_num < 7:
                new_fen += "/"
            row_num += 1
        new_fen += " "
        if self.get_bw() == "w":
            new_fen += "b"
        elif self.get_bw() == "b":
            new_fen += "w"
        new_fen += " "
        new_fen += self.castle
        new_fen += " "
        new_fen += self.en_passent
        new_fen += " "
        new_fen += str(self.half_move)
        new_fen += " "
        new_fen += str(self.full_move)
        self.fen = new_fen

    def get_bw(self):
        """
        Returns if it is black or white to move
        :return: "b" if it is black to move, "w" if it is white to move
        """
        return self.bw

    def get_castle(self):
        """
        Returns castle-string
        :return: String of castling-opportunities
        """
        return self.castle

    def remove_from_castle(self, c):
        """
        Remove castling-rights
        :param c: What to remove (K, Q, k or q)
        :return:
        """
        new_castle = ""
        for cas in self.castle:
            if cas != c:
                new_castle += cas
        if new_castle == "":
            self.castle = "-"
        else:
            self.castle = new_castle

    def get_en_passent(self):
        """
        Returns en-passent
        :return: String with en-passent info
        """
        return self.en_passent

    def get_promoting(self):
        """
        Returns if pawn can promote or not
        :return: boolean. True if pawn can promote
        """
        return self.promoting

    def set_board_array(self):
        """
        Sets board-array
        :return: board-array
        """
        board_array = np.array(
            [np.array(
                [self.Square(row, col) for row in range(8)]
            ) for col in range(8)]
        )
        # Set board-array in each square
        for x in board_array:
            for sqr in x:
                sqr.set_board_array(self)
        return board_array

    def update_board(self):
        """
        Updates pygame-board
        :return:
        """
        self.screen.fill((0, 0, 0))
        self.draw_board()
        self.add_pieces()
        self.draw_pieces()
        if self.status == "w":
            pg.display.set_caption("Chess - White Wins!!!!")
        if self.status == "b":
            pg.display.set_caption("Chess - Black wins!!!!")
        if self.status == "d":
            pg.display.set_caption("Chess - Draw!!!!")
        pg.display.update()

    def draw_board(self):
        """
        Draw chess-board in pygame
        :return:
        """
        colour_dict = {True: WHITE_SQUARE, False: BLACK_SQUARE}
        highlight_dict = {True: HIGHLIGHT_WHITE_SQUARE, False: HIGHLIGHT_BLACK_SQUARE}
        current_colour = True
        for i in range(8):
            for j in range(8):
                # Get square
                sqr = self.board_array[i, j]

                if sqr.is_clicked():
                    sqr.add_visual(pg.draw.rect(
                        self.screen,
                        CLICKED_SQUARE,
                        (
                            int(j * self.h / 8),
                            int(i * self.h / 8),
                            int(self.h / 8),
                            int(self.h / 8)
                        )
                    ))
                elif sqr.is_highlighted():
                    sqr.add_visual(pg.draw.rect(
                        self.screen,
                        highlight_dict[current_colour],
                        (
                            int(j * self.h / 8),
                            int(i * self.h / 8),
                            int(self.h / 8),
                            int(self.h / 8)
                        )
                    ))
                else:
                    sqr.add_visual(pg.draw.rect(
                        self.screen,
                        colour_dict[current_colour],
                        (
                            int(j * self.h / 8),
                            int(i * self.h / 8),
                            int(self.h / 8),
                            int(self.h / 8)
                        )
                    ))
                current_colour = not current_colour
            current_colour = not current_colour

    def draw_pieces(self):
        """
        Draw pieces on chess-board in pygame
        :return:
        """
        for i in range(8):
            for j in range(8):
                if self.get_board_array()[i, j].get_content() is not None:
                    self.screen.blit(
                        self.get_board_array()[i, j].get_content().get_visual(),
                        (int(j * self.h / 8), int(i * self.h / 8))
                    )

    def get_board_array(self):
        """
        Gets board_array
        :return: board_array
        """
        return self.board_array

    def add_pieces(self):
        """
        Adds pieces to board-array
        :return:
        """
        i = 0
        j = 0
        for c in self.fen_pos:
            try:
                a = int(c)
                j += a
            except ValueError:
                if c == "/":
                    i += 1
                    j = 0
                else:
                    self.board_array[i, j].add_content(self.Piece(c))
                    j += 1

    def move_piece(self, fr, to, human=False):
        """
        Moves piece on board
        :param fr: Square to move from
        :param to: Square to move to
        :param human: If player to move are human or not
        :return:
        """
        # Update half-move clock and full-move clock
        self.half_move += 1
        if self.get_bw() == "b":
            self.full_move += 1
        if self.board_array[fr[0], fr[1]].get_content().get_type().lower() == "p":
            self.half_move = 0
        if self.board_array[to[0], to[1]].get_content() is not None:
            self.half_move = 0

        # Move piece
        self.board_array[to[0], to[1]].add_content(
            self.board_array[fr[0], fr[1]].get_content()
        )
        self.board_array[fr[0], fr[1]].add_content()

        # If taking on en-passant
        if self.get_en_passent() != "-":
            if util.array_position_to_string_position(to) == self.get_en_passent():
                if to[0] == 2:
                    self.board_array[3, to[1]].add_content()
                elif to[0] == 5:
                    self.board_array[4, to[1]].add_content()
                self.half_move = 0

        # If castling
        to_content = self.board_array[to[0], to[1]].get_content()
        if "K" in self.castle:
            if to_content is not None:
                if to_content.get_type() == "K" and to[1] - 2 == fr[1]:
                    self.board_array[7, 5].add_content(
                        self.board_array[7, 7].get_content()
                    )
                    self.board_array[7, 7].add_content()
                    self.remove_from_castle("K")
        if "Q" in self.castle:
            if to_content is not None:
                if to_content.get_type() == "K" and to[1] + 2 == fr[1]:
                    self.board_array[7, 3].add_content(
                        self.board_array[7, 0].get_content()
                    )
                    self.board_array[7, 0].add_content()
                    self.remove_from_castle("Q")
        if "k" in self.castle:
            if to_content is not None:
                if to_content.get_type() == "k" and to[1] - 2 == fr[1]:
                    self.board_array[0, 5].add_content(
                        self.board_array[0, 7].get_content()
                    )
                    self.board_array[0, 7].add_content()
                    self.remove_from_castle("k")
        if "q" in self.castle:
            if to_content is not None:
                if to_content.get_type() == "k" and to[1] + 2 == fr[1]:
                    self.board_array[0, 3].add_content(
                        self.board_array[0, 0].get_content()
                    )
                    self.board_array[0, 0].add_content()
                    self.remove_from_castle("q")

        # If king or rook moves from start-pos, remove castle-right
        if to_content is not None:
            if to_content.get_type() == "K" and fr == [7, 4]:
                self.remove_from_castle("K")
                self.remove_from_castle("Q")
            if to_content.get_type() == "k" and fr == [0, 4]:
                self.remove_from_castle("k")
                self.remove_from_castle("q")
            if to_content.get_type() == "R":
                if fr == [7, 0]:
                    self.remove_from_castle("Q")
                if fr == [7, 7]:
                    self.remove_from_castle("K")
            if to_content.get_type() == "r":
                if fr == [0, 0]:
                    self.remove_from_castle("q")
                if fr == [0, 7]:
                    self.remove_from_castle("k")

        # Update en-passant
        self.en_passent = "-"
        if to_content is not None:
            if to_content.get_type() == "P" and to[0] + 2 == fr[0]:
                self.en_passent = util.array_position_to_string_position([fr[0] - 1, fr[1]])
            if to_content.get_type() == "p" and to[0] - 2 == fr[0]:
                self.en_passent = util.array_position_to_string_position([fr[0] + 1, fr[1]])

        # Promote pawn?
        self.promoting = False
        if to[0] == 0 and self.board_array[to[0], to[1]].get_content().get_type() == "P":
            self.promoting = True
            if human:
                self.promote_pawn(to)
        if to[0] == 7 and self.board_array[to[0], to[1]].get_content().get_type() == "p":
            self.promoting = True
            if human:
                self.promote_pawn(to)

    def next_turn(self):
        """
        Setting up next turn
        :return:
        """
        self.new_fen()
        self.set_fen(self.fen)
        if self.get_fen_pos() not in self.positions_in_game:
            self.positions_in_game[self.get_fen_pos()] = 0
        self.positions_in_game[self.get_fen_pos()] += 1

        # Check for win, lose or draw
        self.win_lose_draw()
        self.update_board()
        print(self)
        print(self.get_fen())
        if self.status == "w":
            print("White has won")
        elif self.status == "b":
            print("Black has won")
        elif self.status == "d":
            print("Draw")

    def win_lose_draw(self):
        """
        Checks for win, lose or draw and updates status
        :return:
        """
        white_king_present = False
        black_king_present = False
        other_piece_than_king = False
        check = logic.check(self.get_board_array(), self.get_bw())
        legal_moves = False

        # Go through board to check for moves, check and kings
        for row in self.get_board_array():
            for sqr in row:
                if sqr.get_content() is not None:
                    if sqr.get_content().get_type() == "K":
                        white_king_present = True
                    elif sqr.get_content().get_type() == "k":
                        black_king_present = True
                    else:
                        other_piece_than_king = True
                    if logic.legal_moves(
                        self.get_board_array(),
                        sqr.get_position(),
                        self.get_bw(),
                        self.get_castle(),
                        self.get_en_passent()
                    ):
                        legal_moves = True

        # Sets status
        if not white_king_present:
            self.set_status("b")  # Black has won
        if not black_king_present:
            self.set_status("w")  # White has won
        if not other_piece_than_king:
            self.set_status("d")  # Draw if only kings left
        if not legal_moves and not check:
            self.set_status("d")  # Draw
        if not legal_moves and check:
            if self.get_bw() == "w":
                self.set_status("b")  # White is check-mate, black has won
            elif self.get_bw() == "b":
                self.set_status("w")  # Black is check-mate, white has won
        if self.half_move == 100:
            self.set_status("d")
        if self.positions_in_game[self.get_fen_pos()] == 3:
            self.set_status("d")

    def promote_pawn(self, to, t=""):
        """
        Promotes pawn
        :param to: Square that the pawn has moved to
        :param t: Which type, default is empty string, which means that a human should choose
        :return:
        """
        new_type = t
        loop = True
        while loop:
            if new_type == "":
                new_type = input(
                    """
Promote pawn:
What will you promote your pawn to?
q: Queen
r: Rook
n: Knight
b: Bishop
"""
                )
            if new_type in ["q", "r", "n", "b"]:
                print("Promoting pawn to "+new_type)
                if to[0] == 0:
                    self.board_array[to[0], to[1]].get_content().set_type(new_type.upper())
                if to[0] == 7:
                    self.board_array[to[0], to[1]].get_content().set_type(new_type.lower())
                loop = False
            else:
                print("Invalid new type. Try again!\n\n")
                new_type = ""

    class Square:
        """
        Square in chess-board
        """
        def __init__(self, row, col):
            self.content = None
            self.visual = None
            self.board = None
            self.row = row
            self.col = col
            self.clicked = False
            self.highlighted = False
            self.name = self.set_name()

        def __str__(self):
            if self.content is None:
                return "-"
            return self.content.__str__()

        def set_name(self):
            """
            Sets Name of square. eg. e4
            :return:
            """
            char_dict = {
                0: "a",
                1: "b",
                2: "c",
                3: "d",
                4: "e",
                5: "f",
                6: "g",
                7: "h"
            }
            return char_dict[self.col] + str(8 - self.row)

        def get_name(self):
            """
            Returns name of square. eg. e4
            :return: Name of square as String
            """
            return self.name

        def set_board_array(self, b):
            """
            Sets pointer to board
            :param b: board-object
            :return:
            """
            self.board = b

        def get_board(self):
            """
            Returns board
            :return: board
            """
            return self.board

        def add_visual(self, rect):
            """
            Adds pygame-rectangle
            :param rect: Union[Rect, RectType]
            :return:
            """
            self.visual = rect

        def add_content(self, piece=None):
            """
            Adds piece to square
            :param piece: piece-class, None is default
            :return:
            """
            self.content = piece

        def get_visual(self):
            """
            Returns rect
            :return: Union[Rect, RectType]
            """
            return self.visual

        def get_content(self):
            """
            Returns content
            :return: content of square
            """
            return self.content

        def get_position(self):
            """
            Returns position
            :return: [row, col]
            """
            return [self.col, self.row]

        def click(self):
            """
            Click on this square
            :return:
            """
            # If square is highlighted, MOVE PIECE from previous clicked square
            if self.highlighted:
                for row in self.board.get_board_array():
                    for sq in row:
                        if sq.is_clicked():
                            self.board.move_piece(sq.get_position(), self.get_position(), human=True)
                            self.board.next_turn()
                for row in self.board.get_board_array():
                    for sq in row:
                        sq.un_click()
                        sq.un_highlight()
                return

            # If square is previously clicked, un-click
            if self.clicked:
                self.un_click()
                for row in self.board.get_board_array():
                    for sq in row:
                        if sq.is_highlighted():
                            sq.un_highlight()
                return

            # Else
            # Un-click and un-highlight all squares
            for row in self.board.get_board_array():
                for sq in row:
                    sq.un_click()
                    sq.un_highlight()
            # Click on square
            self.clicked = True
            # Square can't be highlighted and clicked
            self.highlighted = False

            # Highlight all possible moves if this square contains a piece
            if self.content is not None:
                moves = logic.legal_moves(
                    self.board.get_board_array(),
                    self.get_position(),
                    self.board.get_bw(),
                    self.board.get_castle(),
                    self.board.get_en_passent()
                )
                for m in moves:
                    self.board.get_board_array()[self.col + m[0], self.row + m[1]].highlight()

        def un_click(self):
            """
            Un-click this square
            :return:
            """
            self.clicked = False

        def is_clicked(self):
            """
            Get if this square is clicked
            :return: Boolean if this square is clicked
            """
            return self.clicked

        def highlight(self):
            """
            Highlight this square
            :return:
            """
            self.highlighted = True
            # Square can't be highlighted and clicked
            self.clicked = False

        def un_highlight(self):
            """
            Un-highlight this square
            :return:
            """
            self.highlighted = False

        def is_highlighted(self):
            """
            Get if this square is highlighted
            :return: Boolean if this square is highlighted
            """
            return self.highlighted

    class Piece:
        """
        Piece on chess-board
        """
        def __init__(self, t):
            """
            Initializes piece
            :param t: Which type
            """
            self.type = t
            self.visual = set_visual_piece(self.type)

        def __str__(self):
            return self.type

        def get_visual(self):
            """
            Gets image of piece
            :return: image of piece
            """
            return self.visual

        def set_type(self, t):
            """
            Sets new type of piece
            :param t: type to be set
            :return:
            """
            if t.lower() in ["q", "r", "n", "b", "p", "k"]:
                self.type = t
            else:
                raise ValueError("Couldn't set new type for piece")

        def get_type(self):
            """
            Returns type
            :return: type of piece
            """
            return self.type


if __name__ == "__main__":
    print("Running chess_board script")
    width = 60 * 8
    height = 60 * 8
    board = Board(width, height)
    print(board)
    while True:
        for event in pg.event.get():
            # Quitting game
            if event.type == QUIT:
                pg.quit()
                sys.exit()
            # Pressing mouse
            if event.type == MOUSEBUTTONDOWN:
                pos = pg.mouse.get_pos()
                for r in board.get_board_array():
                    for square in r:
                        if square.get_visual().collidepoint(pos):
                            square.click()
                board.update_board()
