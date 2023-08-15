from enum import Enum


class PieceType(Enum):
    EMPTY = 0
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 5
    QUEEN = 9
    KING = float("inf")


class Piece:
    def __init__(self, color: bool):
        self.color = color
        self.piece_type = PieceType.EMPTY
        self.value = 0
        self.as_string = ' '

    def is_empty(self):
        return self.piece_type is PieceType.EMPTY

    def get_value(self):
        return self.value

    def get_moves(self):
        pass

    def is_white(self):
        return self.color

    def get_type(self):
        return self.piece_type

    def print_as_string(self):
        print(self.as_string)
