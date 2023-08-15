import piece


class King(piece.Piece):
    def __init__(self, color: bool):
        super().__init__(color)
        self.value = 9
        self.piece_type = piece.PieceType.KING
        self.as_string = "♔" if color else "♚"
        self.moves = []
        self.moved = False
        self.moves.append((0, 1))
        self.moves.append((1, 0))
        self.moves.append((0, -1))
        self.moves.append((-1, 0))
        self.moves.append((1, 1))
        self.moves.append((-1, 1))
        self.moves.append((1, -1))
        self.moves.append((-1, -1))

    def get_moves(self):
        return self.moves

    def can_castle(self):
        return not self.moved
