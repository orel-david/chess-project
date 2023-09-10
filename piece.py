from enum import Enum


class PieceType(Enum):
    EMPTY = 0
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 5
    QUEEN = 9
    KING = float("inf")

