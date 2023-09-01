import sys
from typing import Optional, Union, Tuple, Sequence

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


def condition(board, cell, move):
    if Utils.is_under_check(board, cell.is_white()):
        if not Utils.check_stops_check(board, cell, move):
            return False

    if cell.get_cell_type() == PieceType.KING:
        if Utils.is_threatened(board, cell.is_white(), board.get_cell(move.row, move.col)):
            return False

    if not Utils.check_stops_check(board, cell, move):
        return False
    return True


class GUI:
    width = 800
    height = 800
    alpha = 128
    legal_color = (0, 255, 0)
    check_color = (255, 0, 0)
    white_pieces = create_image_dict(True, width, height)
    black_pieces = create_image_dict(False, width, height)
    pieces = {True: white_pieces, False: black_pieces}
    origin: Optional[Cell]
    move: Optional[Move]
    white = True
    promotion_case = False
    moves: Optional[Sequence[Move]]
    threats: Optional[Sequence[Cell]]

    def __init__(self):
        pygame.init()
        self.origin = None
        self.move = None
        self.moves = None
        self.threats = None
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
                        cell = board.get_cell(row, col)

                        if self.promotion_case:
                            direction = 1 if self.is_white() else -1
                            queen_option = 8 if self.is_white() else 1
                            if col != self.move.col:
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
                            self.promotion_case = False
                            self.make_move(board, (self.origin, self.move))
                            self.draw_board(board)
                            self.origin = None
                            self.move = None
                            king_cell = board.get_pieces_dict(self.is_white())[PieceType.KING][0]
                            self.threats = Utils.get_threats(board, self.is_white(), king_cell)
                            for threat in self.threats:
                                self.mark_check(threat)
                            return

                        if (not cell.is_empty()) and cell.is_white() == self.is_white():
                            self.set_origin(board, row, col)
                            return

                        if self.origin.get_cell_type() == PieceType.KING:
                            castling_moves = self.get_castle_moves(board)
                            for castle in castling_moves:
                                if castle.row == row and castle.col == col:
                                    self.make_move(board, castle)
                                    self.draw_board(board)
                                    self.origin = None
                                    self.move = None
                                    return

                        if self.origin.get_cell_type() == PieceType.PAWN:
                            promotion_rank = 8 if self.is_white() else 1
                            self.promotion_case = promotion_rank == row

                        self.perform_move(board, row, col, self.promotion_case)
                        king_cell = board.get_pieces_dict(self.is_white())[PieceType.KING][0]
                        self.threats = Utils.get_threats(board, self.is_white(), king_cell)
                        for threat in self.threats:
                            self.mark_check(threat)
                        return

                    print("white" if self.is_white() else "black")
                    self.set_origin(board, row, col)

    def is_in_moves(self, move: Move):
        for m in self.moves:
            if m.row == move.row and m.col == move.col:
                move.is_en_passant = m.is_en_passant
                return True
        return False

    def draw_promotion_selection(self, move: Move):
        color = move.row == 8
        row = 8 if color else 4
        rectangle = pygame.Rect((move.col - 1) * (self.width / 8), (8 - row) * (self.height / 8),
                                self.width / 8 + 5,
                                self.height / 2)
        pygame.draw.rect(self.screen, (200, 222, 255), rectangle)

        # draw the pieces
        row = 8 if color else 1
        direction = 1 if color else -1
        self.draw_at_cell(self.pieces[color][PieceType.QUEEN], row, move.col)
        self.draw_at_cell(self.pieces[color][PieceType.KNIGHT], row - direction, move.col)
        self.draw_at_cell(self.pieces[color][PieceType.ROOK], row - direction * 2, move.col)
        self.draw_at_cell(self.pieces[color][PieceType.BISHOP], row - direction * 3, move.col)

        pygame.display.update()

    def set_origin(self, board: Board, row, col):
        self.promotion_case = False
        self.origin = board.get_cell(row, col)
        self.draw_board(board)
        if self.origin.is_white() != self.is_white():
            self.origin = None
            return
        moves = Utils.get_all_normal_moves(board, self.origin)
        if self.origin.get_cell_type() == PieceType.KING:
            moves += self.get_castle_moves(board)
        self.moves = [m for m in moves if condition(board, self.origin, m)]
        for move in self.moves:
            self.draw_move(board, move)

    def perform_move(self, board, row, col, promote=False):
        self.move = Move(row, col)
        if not self.is_in_moves(self.move):
            self.move = None
            self.set_origin(board, row, col)
            return

        if promote:
            self.draw_board(board)
            self.draw_promotion_selection(self.move)
            return

        self.make_move(board, (self.origin, self.move))
        self.draw_board(board)
        self.origin = None
        self.move = None

    def draw_move(self, board: Board, move: Move):
        if move.row > 8 or move.col > 8 or move.row < 1 or move.col < 1:
            return
        rectangle = pygame.Rect((move.col - 1) * (self.width / 8), (8 - move.row) * (self.height / 8),
                                self.width / 8,
                                self.height / 8)
        surface = pygame.Surface((rectangle.width, rectangle.height), pygame.SRCALPHA)
        cell = board.get_cell(move.row, move.col)
        color = self.legal_color if cell.get_cell_type() == PieceType.EMPTY else (255, 255, 0)
        surface.fill((color[0], color[1], color[2], self.alpha))
        self.screen.blit(surface, rectangle)
        pygame.display.update()

    def mark_check(self, cell: Cell):
        rectangle = pygame.Rect((cell.col - 1) * (self.width / 8), (8 - cell.row) * (self.height / 8),
                                self.width / 8,
                                self.height / 8)
        surface = pygame.Surface((rectangle.width, rectangle.height), pygame.SRCALPHA)
        color = (255, 0, 0)
        surface.fill((color[0], color[1], color[2], self.alpha))
        self.screen.blit(surface, rectangle)
        pygame.display.update()

    def end(self, result):
        if result == 0:
            text = "Stalemate"
        elif result == 1:
            text = 'white won the game'
        else:
            text = 'black won the game'
        font = pygame.font.SysFont('chalkduster.ttf', 72)
        img = font.render(text, True, (255, 0, 0))
        self.screen.blit(img, (300, self.height / 2))
        pygame.display.update()
        pygame.time.delay(2000)

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

    def make_move(self, board: Board, user_input: Union[Move, Tuple[Cell, Move]]):
        try:

            if type(user_input) is Utils.Move:
                Utils.castle(board, self.white, user_input)
                self.white = not self.white
                return

            Utils.make_move(board, user_input[0], user_input[1], True)
            self.white = not self.white
        except NonLegal:
            print("Illegal move, try again")
        except KingSacrifice:
            print("You can't move a locked piece, try again")
        except KingUnderCheck:
            print("You need to move your king out of danger, try again")
        except KingNonLegal:
            print("You can't sacrifice your king, try again")
