from pieces import piece


class Pawn(piece.Piece):
    def __init__(self, color: bool):
        super().__init__(color)
        self.value = 1
        self.piece_type = piece.PieceType.PAWN
        self.as_string = "♙" if color else "♟"
        self.en_passant = False
        self.start = True
        self.moves = [(1, 0)]

    def get_moves(self):
        return self.moves if (not self.start) else (self.moves.append((2, 0)))

