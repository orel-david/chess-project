from pieces import piece


class Rook(piece.Piece):
    def __init__(self, color: bool):
        super().__init__(color)
        self.value = 5
        self.piece_type = piece.PieceType.ROOK
        self.as_string = "♖" if color else "♜"
        self.moved = False
        self.moves = []
        self.moves.append((0, 1))
        self.moves.append((1, 0))
        self.moves.append((0, -1))
        self.moves.append((-1, 0))

    def get_moves(self):
        return self.moves

    def can_castle(self):
        return not self.moved
