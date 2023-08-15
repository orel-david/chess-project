import piece


class Queen(piece.Piece):
    def __init__(self, color: bool):
        super().__init__(color)
        self.value = 9
        self.piece_type = piece.PieceType.QUEEN
        self.as_string = "♕" if color else "♛"
        self.moves = []
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
