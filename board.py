from cell import Cell
from pieces.bishop import Bishop
from pieces.king import King
from pieces.knight import Knight
from pieces.pawn import Pawn
from pieces.piece import Piece, PieceType
from pieces.queen import Queen
from pieces.rook import Rook


def create_start_row(color):
    start = []
    index = 1 if color else 8
    rook_1 = Rook(color)
    rook_2 = Rook(color)
    knight = Knight(color)
    bishop = Bishop(color)
    queen = Queen(color)
    king = King(color)
    start.append(Cell(index, 1, rook_1))
    start.append(Cell(index, 2, knight))
    start.append(Cell(index, 3, bishop))
    start.append(Cell(index, 4, queen))
    start.append(Cell(index, 5, king))
    start.append(Cell(index, 6, bishop))
    start.append(Cell(index, 7, knight))
    start.append(Cell(index, 8, rook_2))
    return start


def create_empty_row(index):
    empty = Piece(True)
    row = []
    for i in range(1, 9):
        cell = Cell(index, i, empty)
        row.append(cell)
    return row


class Board:
    black_pieces = {PieceType.PAWN: [], PieceType.QUEEN: [], PieceType.BISHOP: [], PieceType.KNIGHT: [],
                    PieceType.KING: [], PieceType.ROOK: []}
    white_pieces = {PieceType.PAWN: [], PieceType.QUEEN: [], PieceType.BISHOP: [], PieceType.KNIGHT: [],
                    PieceType.KING: [], PieceType.ROOK: []}
    en_passant_ready = None

    # In the future maybe add support for fen and pgn as init method
    def __init__(self):
        self.board = []
        white_pawn_row = []
        black_pawn_row = []
        for i in range(1, 9):
            black_pawn = Pawn(False)
            white_pawn = Pawn(True)
            black_cell = Cell(7, i, black_pawn)
            self.black_pieces[PieceType.PAWN].append(black_cell)
            white_cell = Cell(2, i, white_pawn)
            self.white_pieces[PieceType.PAWN].append(white_cell)
            white_pawn_row.append(white_cell)
            black_pawn_row.append(black_cell)
        white_start = create_start_row(True)
        black_start = create_start_row(False)
        self.add_row_pieces(white_start)
        self.add_row_pieces(black_start)
        self.board.append(white_start)
        self.board.append(white_pawn_row)
        for i in range(4):
            self.board.append(create_empty_row(3 + i))
        self.board.append(black_pawn_row)
        self.board.append(black_start)

    def add_row_pieces(self, row_pieces):
        for cell in row_pieces:
            if not cell.is_empty():
                if cell.is_white():
                    self.white_pieces[cell.get_cell_type()].append(cell)
                else:
                    self.black_pieces[cell.get_cell_type()].append(cell)

    def get_board(self):
        return self.board

    def get_cell(self, row: int, col: int):
        if row > 8 or col > 8 or row < 1 or col < 1:
            return None
        return self.board[row - 1][col - 1]

    def set_piece(self, row: int, col: int, piece: Piece):
        if row > 8 or col > 8 or row < 1 or col < 1:
            return
        self.board[row - 1][col - 1].change_cell_piece(piece)

    def get_pieces_dict(self, is_white):
        return self.white_pieces if is_white else self.black_pieces

    def print_board(self):
        for row in self.board:
            for cell in row:
                cell.print_cell()

            if row != self.board[-1]:
                print("-" * 20)
