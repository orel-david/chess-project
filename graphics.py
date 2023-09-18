import sys
from typing import Optional, Sequence

import pygame

import Utils
import binary_ops_utils
from Utils import Move
from board import Board
from chess_exceptions import NonLegal, KingSacrifice, KingUnderCheck, KingNonLegal
from piece import PieceType


def create_image_dict(is_white: bool, width: int, height: int):
    """ This function creates a dictionary of pieces' images for a player.

    :param is_white: The player's color
    :param width: The image width
    :param height: The image height
    :return: A dictionary where the key is a PieceType and the value is an image of the piece.
    """

    color = "white" if is_white else "black"
    pieces = {PieceType.PAWN: "pawn", PieceType.QUEEN: "queen", PieceType.BISHOP: "bishop",
              PieceType.KNIGHT: "knight",
              PieceType.KING: "king", PieceType.ROOK: "rook"}
    output_dict = {}
    for piece in pieces.keys():
        img = pygame.image.load("images/{} {}.png".format(color, pieces[piece]))
        img = pygame.transform.scale(img, (width / 8, height / 8))
        output_dict[piece] = img
    return output_dict


class GUI:
    """
    This class handles the game's GUI and provide services such as drawing the board and receiving input from the GUI.
    """
    width = 800
    height = 800
    alpha = 128
    legal_color = (0, 255, 0)
    check_color = (255, 0, 0)
    white_pieces = create_image_dict(True, width, height)
    black_pieces = create_image_dict(False, width, height)
    pieces = {True: white_pieces, False: black_pieces}
    origin: int
    move: Optional[Move]
    white = True
    promotion_case = False
    moves: Optional[Sequence[Move]]
    threats: Sequence[int]

    def __init__(self):
        """
        This method initialize the necessary fields for the class and the pygame module which we use.
        """
        pygame.init()
        self.origin = -1
        self.move = None
        self.moves = None
        self.threats = []
        pygame.display.set_caption("Chess game")
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.board_image = pygame.image.load("images/empty-board.png")
        self.board_image = pygame.transform.scale(self.board_image, (self.width, self.height))
        self.screen.blit(self.board_image, (0, 0))
        pygame.display.update()

    def is_white(self):
        """ Returns if it's white's turn

        :return: True if white's turn
        """
        return self.white

    def draw_at_cell(self, img, cell: int):
        """ This method draws an image on a specific cell

        :param img: The image we want to draw, normally a piece
        :param cell: The cell index
        """

        row, col = binary_ops_utils.translate_cell_to_row_col(cell)
        row += 1
        col += 1
        if row > 8 or col > 8 or row < 1 or col < 1:
            return
        self.screen.blit(img, ((col - 1) * (self.width / 8), (8 - row) * (self.height / 8)))

    def draw_board(self, board: Board):
        """ This method draws the game on the screen and marks the threats in red.

        :param board: The board which we draw
        """
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.board_image, (0, 0))

        for color in self.pieces.keys():
            pieces_dict = board.get_pieces_dict(color)
            for piece in pieces_dict.keys():
                for cell in pieces_dict[piece]:
                    self.draw_at_cell(self.pieces[color][piece], cell)

        self.threats = Utils.get_threats(board)
        for threat in self.threats:
            self.mark_check(threat)
        pygame.display.update()

    def handle_events(self, board: Board):
        """ This is the method which is being called in the main loops and handles all the events of the GUI.

        :param board: The board which we use for inputting moves.
        """

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.WINDOWFOCUSLOST:
                pygame.display.iconify()
            elif event.type == pygame.WINDOWFOCUSGAINED:
                pygame.display.update()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.dict['button'] == 1:
                    # In left click case we need to recognize where the user clicked.
                    x, y = event.dict['pos']
                    col = 1 + int((x * 8) / self.width)
                    row = 8 - int((y * 8) / self.height)

                    if self.origin != -1:
                        # If there is already an origin cell this is an attempt to perform a move.
                        cell = binary_ops_utils.translate_row_col_to_cell(row, col)

                        # If there was a promotion move now the user choose the promotion piece.
                        if self.promotion_case:
                            direction = 1 if self.is_white() else -1
                            queen_option = 8 if self.is_white() else 1
                            if col != self.move.target % 8:
                                self.set_origin(board, row, col)

                            if row == queen_option:
                                self.move.set_promotion(PieceType.QUEEN)
                            elif row == queen_option - direction:
                                self.move.set_promotion(PieceType.KNIGHT)
                            elif row == queen_option - direction * 2:
                                self.move.set_promotion(PieceType.ROOK)
                            elif row == queen_option - direction * 3:
                                self.move.set_promotion(PieceType.BISHOP)
                            else:
                                self.set_origin(board, row, col)
                                return

                            # Now we make the move if legal and draw the board.
                            self.promotion_case = False
                            self.make_move(board, self.move)
                            self.draw_board(board)
                            self.origin = -1
                            self.move = None
                            self.threats = Utils.get_threats(board)
                            for threat in self.threats:
                                self.mark_check(threat)
                            return

                        if board.is_cell_colored(cell, self.is_white()):
                            self.set_origin(board, row, col)
                            return

                        origin_type = board.get_cell_type(self.origin)
                        if origin_type == PieceType.KING:
                            castling_moves = self.get_castle_moves(board)
                            for castle in castling_moves:
                                if castle.target == binary_ops_utils.translate_row_col_to_cell(row, col):
                                    self.make_move(board, castle)
                                    self.draw_board(board)
                                    self.origin = -1
                                    self.move = None
                                    return

                        if origin_type == PieceType.PAWN:
                            promotion_rank = 8 if self.is_white() else 1
                            self.promotion_case = promotion_rank == row

                        self.perform_move(board, row, col, self.promotion_case)
                        return

                    # The other case is that we set the origin cell and draw possible moves for the piece.
                    self.set_origin(board, row, col)

    def is_in_moves(self, move: Move):
        """ Method to validate moves.

        :param move: The move we validate
        :return: Whether the move is in the legal options or not
        """

        for m in self.moves:
            if m.target == move.target:
                return True
        return False

    def draw_promotion_selection(self, move: Move):
        """ This method draw the promotion selection menu when a promotion move is performed.

        :param move: The promotion move
        """

        color = int(move.target / 8) == 7
        row = 8 if color else 4
        col = move.target % 8
        rectangle = pygame.Rect(col * (self.width / 8), (8 - row) * (self.height / 8),
                                self.width / 8 + 5,
                                self.height / 2)
        pygame.draw.rect(self.screen, (200, 222, 255), rectangle)

        # draw the pieces
        row = 8 if color else 1
        direction = 1 if color else -1
        col += 1
        self.draw_at_cell(self.pieces[color][PieceType.QUEEN], binary_ops_utils.translate_row_col_to_cell(row, col))
        self.draw_at_cell(self.pieces[color][PieceType.KNIGHT],
                          binary_ops_utils.translate_row_col_to_cell(row - direction, col))
        self.draw_at_cell(self.pieces[color][PieceType.ROOK],
                          binary_ops_utils.translate_row_col_to_cell(row - 2 * direction, col))
        self.draw_at_cell(self.pieces[color][PieceType.BISHOP],
                          binary_ops_utils.translate_row_col_to_cell(row - 3 * direction, col))

        pygame.display.update()

    def set_origin(self, board: Board, row, col):
        """ This method update the screen for a new origin cell.

        :param board: The board which we draw
        :param row: The new origin row
        :param col: The new origin column
        """
        self.promotion_case = False
        self.origin = binary_ops_utils.translate_row_col_to_cell(row, col)
        self.draw_board(board)

        if not board.is_cell_colored(self.origin, self.is_white()):
            self.origin = -1
            return

        origin_type = board.get_cell_type(self.origin)
        self.moves = Utils.get_all_legal_moves(board, self.origin, origin_type, self.is_white())
        for move in self.moves:
            self.draw_move(board, move)

    def perform_move(self, board, row, col, promote=False):
        """ This method receive the target's cell coordinates and make a move with that target and the origin cell

        :param board: The board which we perform the move on
        :param row: The row of the target cell
        :param col: the column of the target cell
        :param promote: Flag to tell whether this is a promotion move
        """

        target = binary_ops_utils.translate_row_col_to_cell(row, col)
        self.move = Move(self.origin, target)
        if not self.is_in_moves(self.move):
            self.move = None
            self.set_origin(board, row, col)
            return

        if promote:
            self.draw_board(board)
            self.draw_promotion_selection(self.move)
            return

        self.make_move(board, self.move)
        self.draw_board(board)
        self.origin = -1
        self.move = None

    def draw_move(self, board: Board, move: Move):
        """ This method draws a move on the board in green if it's on empty cell and in yellow if it is a capture

        :param board: The board we use
        :param move: The move we draw
        """

        if move.target & 0x40 != 0:
            return

        row, col = binary_ops_utils.translate_cell_to_row_col(move.target)
        row += 1
        col += 1
        rectangle = pygame.Rect((col - 1) * (self.width / 8), (8 - row) * (self.height / 8),
                                self.width / 8,
                                self.height / 8)
        surface = pygame.Surface((rectangle.width, rectangle.height), pygame.SRCALPHA)
        color = self.legal_color if board.is_cell_empty(move.target) else (255, 255, 0)
        surface.fill((color[0], color[1], color[2], self.alpha))
        self.screen.blit(surface, rectangle)
        pygame.display.update()

    def mark_check(self, cell: int):
        """ This draws a red mark on a cell of a piece that threatens the king

        :param cell: The cell of the threatening piece
        """

        row, col = binary_ops_utils.translate_cell_to_row_col(cell)
        row += 1
        col += 1
        rectangle = pygame.Rect((col - 1) * (self.width / 8), (8 - row) * (self.height / 8),
                                self.width / 8,
                                self.height / 8)
        surface = pygame.Surface((rectangle.width, rectangle.height), pygame.SRCALPHA)
        color = (255, 0, 0)
        surface.fill((color[0], color[1], color[2], self.alpha))
        self.screen.blit(surface, rectangle)
        pygame.display.update()

    def end(self, result):
        """ This method draws the end game prompt on the screen

        :param result: The game result from gui_game
        """
        font = pygame.font.SysFont('chalkduster.ttf', 72)
        if result == 0:
            img = font.render("Stalemate", True, (255, 0, 0))
            self.screen.blit(img, (300, self.height / 2))
        elif result == 1:
            img = font.render('white won the game', True, (255, 0, 0))
            self.screen.blit(img, (150, self.height / 2))
        else:
            img = font.render('black won the game', True, (255, 0, 0))
            self.screen.blit(img, (150, self.height / 2))
        pygame.display.update()
        pygame.time.delay(2000)

    def get_castle_moves(self, board: Board):
        """
        That method returns all castling moves for the player playing.
        """
        return Utils.get_castle_moves(board, self.is_white())

    def make_move(self, board: Board, user_input: Move):
        """
        This method perform a move on the board.
        """
        try:

            Utils.make_move(board, user_input)
            self.white = not self.white

        except NonLegal:
            print("Illegal move, try again")
        except KingSacrifice:
            print("You can't move a locked piece, try again")
        except KingUnderCheck:
            print("You need to move your king out of danger, try again")
        except KingNonLegal:
            print("You can't sacrifice your king, try again")
