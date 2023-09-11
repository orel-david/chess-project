import binary_ops_utils
from piece import PieceType


class Board:
    pieces_dict = {'q': PieceType.QUEEN, 'r': PieceType.ROOK, 'b': PieceType.BISHOP, 'n': PieceType.KNIGHT,
                   'k': PieceType.KING, 'p': PieceType.PAWN}
    castling_options = ''
    is_white: bool
    en_passant_ready = 0
    count = 0
    board = 0
    white_board = 0
    black_board = 0
    pawn_moves = []
    knight_moves = []
    king_moves = []
    vertical_distances = []
    directions = [1, -1, 8, -8, 7, -7, 9, -9]
    piece_maps = {PieceType.PAWN: 0, PieceType.QUEEN: 0, PieceType.BISHOP: 0, PieceType.KNIGHT: 0,
                  PieceType.KING: 0, PieceType.ROOK: 0}

    def __init__(self):
        self.black_pieces = {PieceType.PAWN: [], PieceType.QUEEN: [], PieceType.BISHOP: [], PieceType.KNIGHT: [],
                             PieceType.KING: [], PieceType.ROOK: []}
        self.white_pieces = {PieceType.PAWN: [], PieceType.QUEEN: [], PieceType.BISHOP: [], PieceType.KNIGHT: [],
                             PieceType.KING: [], PieceType.ROOK: []}
        self.update_distances()
        self.update_pawn_moves()
        self.update_knight_moves()
        self.update_king_moves()
        self.import_from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    def import_from_fen(self, fen_string: str):
        self.black_pieces = {PieceType.PAWN: [], PieceType.QUEEN: [], PieceType.BISHOP: [], PieceType.KNIGHT: [],
                             PieceType.KING: [], PieceType.ROOK: []}
        self.white_pieces = {PieceType.PAWN: [], PieceType.QUEEN: [], PieceType.BISHOP: [], PieceType.KNIGHT: [],
                             PieceType.KING: [], PieceType.ROOK: []}
        parts = fen_string.split()
        rows = parts[0].split("/")
        rows.reverse()
        self.is_white = True if parts[1].lower() == 'w' else False
        self.castling_options = parts[2]
        self.en_passant_ready = 0 if parts[3] == "-" else binary_ops_utils.translate_row_col_to_cell(
            int(parts[3][1]) - 1, ord(parts[3][0].lower()) - ord('a'))
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
            return
        row = row - 1
        col = col - 1
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
        row = row - 1
        col = col - 1
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
        row = row - 1
        col = col - 1
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
            self.black_board = binary_ops_utils.switch_cell_bit(self.black_board, cell, True)

    def remove_cell_piece(self, cell: int, piece: PieceType, is_white: bool):
        self.board = binary_ops_utils.switch_cell_bit(self.board, cell, False)
        self.piece_maps[piece] = binary_ops_utils.switch_cell_bit(self.piece_maps[piece], cell, False)
        if is_white:
            self.white_pieces[piece] = [c for c in self.white_pieces[piece] if c != cell]
            self.white_board = binary_ops_utils.switch_cell_bit(self.white_board, cell, False)
        else:
            self.black_pieces[piece] = [c for c in self.black_pieces[piece] if c != cell]
            self.black_board = binary_ops_utils.switch_cell_bit(self.black_board, cell, False)

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
        self.en_passant_ready = binary_ops_utils.translate_row_col_to_cell(row, col)

    def get_en_passant(self):
        return self.en_passant_ready

    def is_type_of(self, cell: int, piece: PieceType):
        return (self.piece_maps[piece] & (1 << cell)) != 0

    def get_type(self, row: int, col: int):
        if row > 8 or col > 8 or row < 1 or col < 1:
            return
        row = row - 1
        col = col - 1
        for piece in self.piece_maps.keys():
            if (self.piece_maps[piece] & (1 << (row * 8 + col))) != 0:
                return piece
        return PieceType.EMPTY

    def get_cell_type(self, cell: int):
        for piece in self.piece_maps.keys():
            if (self.piece_maps[piece] & (1 << cell)) != 0:
                return piece
        return PieceType.EMPTY

    def update_pawn_moves(self):
        white_moves = []
        black_moves = []
        for i in range(8):
            for j in range(8):
                white_val = 0
                black_val = 0
                white_options = filter(lambda t: binary_ops_utils.translate_row_col_to_cell(t[0] + 1, t[1] + 1) != -1,
                                       [(i + 1, j + 1), (i + 1, j - 1)])
                black_options = filter(lambda t: binary_ops_utils.translate_row_col_to_cell(t[0] + 1, t[1] + 1) != -1,
                                       [(i - 1, j + 1), (i - 1, j - 1)])
                for option in white_options:
                    white_val = binary_ops_utils.switch_cell_bit(white_val, option[0] * 8 + option[1], True)
                for option in black_options:
                    black_val = binary_ops_utils.switch_cell_bit(black_val, option[0] * 8 + option[1], True)
                white_moves.append(white_val)
                black_moves.append(black_val)

        self.pawn_moves.append(white_moves)
        self.pawn_moves.append(black_moves)

    def get_pawn_moves(self, cell: int, is_white: bool):
        captures = self.pawn_moves[0] if is_white else self.pawn_moves[1]
        board = self.black_board if is_white else self.white_board
        pawn_advancement = 8 if is_white else -8
        start_row = 1 if is_white else 6
        en_passant_row = 4 if is_white else 5
        row = cell / 8
        captures = captures[cell] & board
        forward = cell + pawn_advancement
        moves = 0
        if 0 <= forward < 64:
            moves = binary_ops_utils.switch_cell_bit(0, forward, True)
            forward = forward + pawn_advancement
            if 0 <= forward < 64:
                moves = binary_ops_utils.switch_cell_bit(moves, forward, row == start_row)
        moves = moves & (~self.board)
        if self.en_passant_ready != 0 and row == en_passant_row:
            if cell + 1 == self.en_passant_ready:
                moves = binary_ops_utils.switch_cell_bit(moves, cell + 9, True)
            elif cell - 1 == self.en_passant_ready:
                moves = binary_ops_utils.switch_cell_bit(moves, cell + 7, True)

        return moves | captures

    def update_knight_moves(self):
        moves = [(2, 1), (2, -1), (-2, 1), (-2, -1),
                 (1, 2), (-1, 2), (1, -2), (-1, -2)]
        for i in range(8):
            for j in range(8):
                val = 0
                options = []
                for move in moves:
                    if binary_ops_utils.translate_row_col_to_cell(move[0] + i + 1, move[1] + j + 1) != -1:
                        options.append((move[0] + i, move[1] + j))

                for option in options:
                    val = binary_ops_utils.switch_cell_bit(val, option[0] * 8 + option[1], True)
                self.knight_moves.append(val)

    def update_king_moves(self):
        moves = [(0, 1), (0, -1), (1, 1), (-1, -1),
                 (1, -1), (-1, 1), (1, 0), (-1, 0)]
        for i in range(8):
            for j in range(8):
                val = 0
                options = []
                for move in moves:
                    if binary_ops_utils.translate_row_col_to_cell(move[0] + i + 1, move[1] + j + 1) != -1:
                        options.append((move[0] + i, move[1] + j))

                for option in options:
                    val = binary_ops_utils.switch_cell_bit(val, option[0] * 8 + option[1], True)
                self.king_moves.append(val)

    def get_king_cell_moves(self, cell: int):
        return self.king_moves[cell]

    def get_knight_moves(self, row: int, col: int, is_white: bool):
        cell = binary_ops_utils.translate_row_col_to_cell(row, col)
        if cell == -1 or (not self.is_type_of(cell, PieceType.KNIGHT)):
            return []
        board = self.white_board if is_white else self.black_board
        return self.knight_moves[cell] & (~board)

    def get_knight_cell_moves(self, cell: int, is_white):
        board = self.white_board if is_white else self.black_board
        return self.knight_moves[cell] & (~board)

    def update_distances(self):
        for i in range(8):
            for j in range(8):
                north = 7 - i
                south = i
                west = j
                east = 7 - j
                self.vertical_distances.append((east, west, north, south,
                                                min(north, west), min(south, east), min(north, east), min(south, west)))

    def get_vertical_cell_moves(self, cell: int, piece: PieceType, is_white: bool):
        start = 4 if piece == PieceType.BISHOP else 0
        end = 4 if piece == PieceType.ROOK else 8
        result = 0
        for i in range(start, end):
            direction = self.directions[i]
            for j in range(self.vertical_distances[cell][i]):
                target = direction * (j + 1) + cell

                if self.is_cell_colored(target, is_white):
                    break

                result = binary_ops_utils.switch_cell_bit(result, target, True)

                if not self.is_cell_empty(target):
                    break
        return result

    def get_moves_by_cell(self, cell: int, is_white: bool):
        piece = self.get_cell_type(cell)
        if self.is_cell_empty(cell):
            return
        if piece == PieceType.PAWN:
            return self.get_pawn_moves(cell, is_white)
        elif piece == PieceType.KING:
            return self.get_king_cell_moves(cell)
        elif piece == PieceType.KNIGHT:
            return self.get_knight_cell_moves(cell, is_white)
        return self.get_vertical_cell_moves(cell, piece, is_white)

    def get_distances(self):
        return self.vertical_distances
