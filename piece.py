from enum import Enum


# Enum of all the pieces where the value is the piece value.
class PieceType(Enum):
    EMPTY = 0
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 5
    QUEEN = 9
    KING = float("inf")
