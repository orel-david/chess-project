from cell import Cell
from pieces.bishop import Bishop
from pieces.king import King
from pieces.knight import Knight
from pieces.pawn import Pawn
from pieces.piece import Piece
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
    def __init__(self):
        self.board = []
        white_pawn_row = []
        black_pawn_row = []
        for i in range(1, 9):
            black_pawn = Pawn(False)
            white_pawn = Pawn(True)
            black_cell = Cell(7, i, black_pawn)
            white_cell = Cell(2, i, white_pawn)
            white_pawn_row.append(white_cell)
            black_pawn_row.append(black_cell)
        white_start = create_start_row(True)
        black_start = create_start_row(False)
        self.board.append(white_start)
        self.board.append(white_pawn_row)
        for i in range(4):
            self.board.append(create_empty_row(3 + i))
        self.board.append(black_pawn_row)
        self.board.append(black_start)

    def get_board(self):
        return self.board

    def get_cell(self, row: int, col: int):
        return self.board[row - 1][col - 1]

    def print_board(self):
        for row in self.board:
            for cell in row:
                cell.print_cell()

            if row != self.board[-1]:
                print("-" * 20)

