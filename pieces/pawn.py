from pieces import piece


class Pawn(piece.Piece):
    def __init__(self, color: bool):
        super().__init__(color)
        self.value = 1
        self.piece_type = piece.PieceType.PAWN
        self.as_string = "♙" if color else "♟"
        self.an_passant = True
        self.start = True
        self.moves = [(0, 1)]

    def get_moves(self):
        return self.moves if (not self.start) else (self.moves.append((0, 2)))

    def can_an_passant(self):
        return self.an_passant
