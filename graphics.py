import sys
from typing import Optional, Union, Tuple

import pygame

import Utils
from Utils import Move
from board import Board
from cell import Cell
from chess_exceptions import NonLegal, KingSacrifice, KingUnderCheck, KingNonLegal
from pieces.piece import PieceType


def create_image_dict(is_white: bool, width: int, height: int):
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
    width = 800
    height = 800
    white_pieces = create_image_dict(True, width, height)
    black_pieces = create_image_dict(False, width, height)
    pieces = {True: white_pieces, False: black_pieces}
    origin: Optional[Cell]
    move: Optional[Move]
    white = True

    def __init__(self):
        pygame.init()
        self.origin = None
        self.move = None
        pygame.display.set_caption("Chess game")
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.board_image = pygame.image.load("images/empty-board.png")
        self.board_image = pygame.transform.scale(self.board_image, (self.width, self.height))
        self.screen.blit(self.board_image, (0, 0))
        pygame.display.update()

    def is_white(self):
        return self.white

    def draw_at_cell(self, img, row: int, col: int):
        if row > 8 or col > 8 or row < 1 or col < 1:
            return
        self.screen.blit(img, ((col - 1) * (self.width / 8), (8 - row) * (self.height / 8)))

    def draw_board(self, board: Board):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.board_image, (0, 0))
        for color in self.pieces.keys():
            pieces_dict = board.get_pieces_dict(color)
            for piece in pieces_dict.keys():
                for cell in pieces_dict[piece]:
                    self.draw_at_cell(self.pieces[color][cell.get_cell_type()], cell.get_row(), cell.get_col())
        pygame.display.update()

    def handle_events(self, board: Board):
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
                    x, y = event.dict['pos']
                    col = 1 + int((x * 8) / self.width)
                    row = 8 - int((y * 8) / self.height)
                    if self.origin is not None:
                        if self.origin.get_cell_type() == PieceType.KING:
                            castling_moves = self.get_castle_moves(board)
                            for castle in castling_moves:
                                if castle.row == row and castle.col == col:
                                    self.make_move(board, castle)
                                    self.draw_board(board)
                                    self.origin = None
                                    self.move = None
                                    return
                        else:
                            # TODO: handle promotion
                            self.move = Move(row, col)
                            print("target {} {}".format(self.move.row, self.move.col))
                            self.make_move(board, (Move(self.origin.get_row(), self.origin.get_col()), self.move))
                            self.draw_board(board)
                            self.origin = None
                            self.move = None
                            return

                    self.origin = board.get_cell(row, col)
                    print("origin {} {}".format(self.origin.get_row(), self.origin.get_col()))
                    # TODO: draw possible moves
                    self.draw_board(board)

    def draw_move(self, board: Board, move: Move):
        pass

    def mark_check(self, board: Board, cell: Cell):
        pass

    def end(self, result):
        pass

    def get_castle_moves(self, board: Board):
        moves = []
        row = 1 if self.is_white() else 8
        move_1 = Move(row, 7)
        move_1.set_castle(True)
        if Utils.can_castle(board, self.is_white(), move_1):
            moves.append(move_1)
        move_2 = Move(row, 3)
        move_2.set_castle(False)
        if Utils.can_castle(board, self.is_white(), move_2):
            moves.append(move_2)
        return moves

    def make_move(self, board: Board, user_input: Union[Move, Tuple[Move, Move]]):
        try:

            if type(user_input) is Utils.Move:
                Utils.castle(board, self.white, user_input)
                self.white = not self.white
                return

            origin_cell = board.get_cell(user_input[0].row, user_input[0].col)
            if origin_cell is None:
                return

            if origin_cell.is_white() != self.white:
                print("You must move your pieces")
                return

            if origin_cell.get_cell_type() == PieceType.EMPTY:
                print("You can't move empty cell")
                return

            Utils.make_move(board, origin_cell, user_input[1])
            self.white = not self.white
        except NonLegal:
            print("Illegal move, try again")
        except KingSacrifice:
            print("You can't move a locked piece, try again")
        except KingUnderCheck:
            print("You need to move your king out of danger, try again")
        except KingNonLegal:
            print("You can't sacrifice your king, try again")
