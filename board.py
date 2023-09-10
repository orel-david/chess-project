import binary_ops_utils
from piece import PieceType


class Board:
    black_pieces = {PieceType.PAWN: [], PieceType.QUEEN: [], PieceType.BISHOP: [], PieceType.KNIGHT: [],
                    PieceType.KING: [], PieceType.ROOK: []}
    white_pieces = {PieceType.PAWN: [], PieceType.QUEEN: [], PieceType.BISHOP: [], PieceType.KNIGHT: [],
                    PieceType.KING: [], PieceType.ROOK: []}
    pieces_dict = {'q': PieceType.QUEEN, 'r': PieceType.ROOK, 'b': PieceType.BISHOP, 'n': PieceType.KNIGHT,
                   'k': PieceType.KING, 'p': PieceType.PAWN}
    castling_options = ''
    is_white: bool
    en_passant_ready = 0
    count = 0
    board = 0
    white_board = 0
    black_board = 0
    piece_maps = {PieceType.PAWN: 0, PieceType.QUEEN: 0, PieceType.BISHOP: 0, PieceType.KNIGHT: 0,
                  PieceType.KING: 0, PieceType.ROOK: 0}

    def __init__(self):
        self.import_from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    def import_from_fen(self, fen_string: str):
        parts = fen_string.split()
        rows = parts[0].split("/")
        rows.reverse()
        self.is_white = True if parts[1].lower() == 'w' else False
        self.castling_options = parts[2]
        self.en_passant_ready = 0 if parts[3] == "-" else binary_ops_utils.switch_bit(0, int(parts[3][1]) - 1,
                                                                                      ord(parts[3][0].lower()) - ord(
                                                                                          'a'), True)
        for i in range(8):
            j = 0
            row = rows[i]
            for letter in row:
                if letter.isdigit():
                    j += int(letter)
                else:
                    piece_type = self.pieces_dict[letter.lower()]
                    self.piece_maps[piece_type] = binary_ops_utils.switch_bit(self.piece_maps[piece_type], i, j, True)

                    if letter.islower():
                        self.black_pieces[piece_type].append(i * 8 + j)
                        self.board = binary_ops_utils.switch_bit(self.board, i, j, True)
                        self.black_board = binary_ops_utils.switch_bit(self.black_board, i, j, True)
                    else:
                        self.white_pieces[piece_type].append(i * 8 + j)
                        self.board = binary_ops_utils.switch_bit(self.board, i, j, True)
                        self.white_board = binary_ops_utils.switch_bit(self.white_board, i, j, True)

                    j += 1

    def get_board(self):
        return self.board

    def get_board_by_color(self, is_white: bool):
        return self.white_board if is_white else self.black_board

    def is_empty(self, row: int, col: int):
        if row > 8 or col > 8 or row < 1 or col < 1:
            raise
        return (self.board & (1 << (row * 8 + col))) == 0

    def is_cell_empty(self, cell: int):
        return (self.board & (1 << cell)) == 0

    def is_colored(self, row: int, col: int, is_white: bool):
        if row > 8 or col > 8 or row < 1 or col < 1:
            return
        board = self.white_board if is_white else self.black_board
        return (board & (1 << (row * 8 + col))) != 0

    def is_cell_colored(self, cell: int, is_white: bool):
        board = self.white_board if is_white else self.black_board
        return (board & (1 << cell)) != 0

    def set_piece(self, row: int, col: int, piece: PieceType, is_white: bool):
        if row > 8 or col > 8 or row < 1 or col < 1:
            return
        self.board = binary_ops_utils.switch_bit(self.board, row, col, True)
        self.piece_maps[piece] = binary_ops_utils.switch_bit(self.piece_maps[piece], row, col, True)
        if is_white:
            self.white_pieces[piece].append(row * 8 + col)
            self.white_board = binary_ops_utils.switch_bit(self.white_board, row, col, True)
        else:
            self.black_pieces[piece].append(row * 8 + col)
            self.black_board = binary_ops_utils.switch_bit(self.black_board, row, col, True)

    def remove_piece(self, row: int, col: int, piece: PieceType, is_white: bool):
        if row > 8 or col > 8 or row < 1 or col < 1:
            return
        self.board = binary_ops_utils.switch_bit(self.board, row, col, False)
        self.piece_maps[piece] = binary_ops_utils.switch_bit(self.piece_maps[piece], row, col, False)
        if is_white:
            self.white_pieces[piece] = [c for c in self.white_pieces[piece] if c != (row * 8 + col)]
            self.white_board = binary_ops_utils.switch_bit(self.white_board, row, col, False)
        else:
            self.black_pieces[piece] = [c for c in self.black_pieces[piece] if c != (row * 8 + col)]
            self.black_board = binary_ops_utils.switch_bit(self.black_board, row, col, False)

    def set_cell_piece(self, cell: int, piece: PieceType, is_white: bool):
        self.board = binary_ops_utils.switch_cell_bit(self.board, cell, True)
        self.piece_maps[piece] = binary_ops_utils.switch_cell_bit(self.piece_maps[piece], cell, True)
        if is_white:
            self.white_pieces[piece].append(cell)
            self.white_board = binary_ops_utils.switch_cell_bit(self.white_board, cell, True)
        else:
            self.black_pieces[piece].append(cell)
            self.black_board = binary_ops_utils.switch_bit(self.black_board, cell, True)

    def remove_cell_piece(self, cell: int, piece: PieceType, is_white: bool):
        self.board = binary_ops_utils.switch_bit(self.board, cell, False)
        self.piece_maps[piece] = binary_ops_utils.switch_cell_bit(self.piece_maps[piece], cell, False)
        if is_white:
            self.white_pieces[piece] = [c for c in self.white_pieces[piece] if c != cell]
            self.white_board = binary_ops_utils.switch_bit(self.white_board, cell, False)
        else:
            self.black_pieces[piece] = [c for c in self.black_pieces[piece] if c != cell]
            self.black_board = binary_ops_utils.switch_bit(self.black_board, cell, False)

    def get_pieces_dict(self, is_white):
        return self.white_pieces if is_white else self.black_pieces

    def is_insufficient(self):
        if self.white_pieces[PieceType.PAWN] == [] and self.black_pieces[PieceType.PAWN] == []:
            if len(self.white_pieces[PieceType.ROOK] + self.white_pieces[PieceType.QUEEN]) == 0 and len(
                    self.white_pieces[PieceType.BISHOP] + self.white_pieces[PieceType.KNIGHT]) <= 1:
                return len(self.black_pieces[PieceType.ROOK] + self.black_pieces[PieceType.QUEEN]) == 0 and len(
                    self.black_pieces[PieceType.BISHOP] + self.black_pieces[PieceType.KNIGHT]) <= 1
        return False

    def update_en_passant(self, row: int, col: int):
        self.en_passant_ready = binary_ops_utils.switch_bit(0, row, col, True)

    def get_en_passant(self):
        return self.en_passant_ready

    def is_type_of(self, cell: int, piece: PieceType):
        return (self.piece_maps[piece] & (1 << cell)) != 0

    def get_type(self, row: int, col: int):
        if row > 8 or col > 8 or row < 1 or col < 1:
            return
        for piece in self.piece_maps.keys():
            if (self.piece_maps[piece] & (1 << (row * 8 + col))) != 0:
                return piece
        return PieceType.EMPTY


board = Board()
