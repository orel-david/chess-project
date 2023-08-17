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

    def get_cell_type(self):
        return self.cell_piece.get_type()

    def is_white(self):
        return self.cell_piece.is_white()

    def get_row(self):
        return self.row

    def get_col(self):
        return self.col

    def set_row(self, row):
        self.row = row

    def set_col(self, col):
        self.col = col

    def change_cell_piece(self, piece: Piece):
        self.cell_piece = piece

    def print_cell(self):
        line = self.cell_piece.as_string if (self.col == 1) else "|{}".format(
            self.cell_piece.as_string)
        if self.col == 8:
            print(line)
        else:
            print(line, end="")
