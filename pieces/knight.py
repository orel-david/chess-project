from pieces import piece


class Knight(piece.Piece):
    def __init__(self, color: bool):
        super().__init__(color)
        self.value = 3
        self.piece_type = piece.PieceType.KNIGHT
        self.as_string = "♞" if color else "♘"
        self.moves = [(2, 1), (2, -1), (-2, 1), (-2, -1),
                      (1, 2), (-1, 2), (1, -2), (-1, -2)]

    def get_moves(self):
        return self.moves
