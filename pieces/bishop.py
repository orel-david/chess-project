import piece


class Bishop(piece.Piece):
    def __init__(self, color: bool):
        super().__init__(color)
        self.value = 3
        self.piece_type = piece.PieceType.BISHOP
        self.as_string = "♗" if color else "♝"
        self.moves = []
        self.moves.append((1, 1))
        self.moves.append((-1, 1))
        self.moves.append((1, -1))
        self.moves.append((-1, -1))

    def get_moves(self):
        return self.moves
