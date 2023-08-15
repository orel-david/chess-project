from pieces.piece import PieceType
from pieces.piece import Piece


class Cell:
    def __init__(self, row, col, cell_piece: Piece):
        self.row = row
        self.col = col
        self.cell_piece = cell_piece

    def is_empty(self):
        return self.cell_piece.is_empty()

    def get_cell_piece(self):
        return self.cell_piece

    def get_row(self):
        return self.row

    def get_col(self):
        return self.col

    def print_cell(self):
        line = self.cell_piece.as_string if ((self.col > 1) and (self.col < 8)) else "|{}|".format(
            self.cell_piece.as_string)
        print(line, end="")
