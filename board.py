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
    sliding = 0
    sliding_attacks = 0
    attackers = [0, 0]
    pin_in_position = False
    # change main key to be index
    attackers_maps = {PieceType.PAWN: [0, 0], PieceType.QUEEN: [0, 0], PieceType.BISHOP: [0, 0],
                      PieceType.KNIGHT: [0, 0],
                      PieceType.KING: [0, 0], PieceType.ROOK: [0, 0]}
    pin_map = 0
    check_map = 0
    position_in_check = False
    position_in_double_check = False
    piece_maps = {PieceType.PAWN: 0, PieceType.QUEEN: 0, PieceType.BISHOP: 0, PieceType.KNIGHT: 0,
                  PieceType.KING: 0, PieceType.ROOK: 0}
    threats = []

    def __init__(self):
        self.black_pieces = {PieceType.PAWN: [], PieceType.QUEEN: [], PieceType.BISHOP: [], PieceType.KNIGHT: [],
                             PieceType.KING: [], PieceType.ROOK: []}
        self.white_pieces = {PieceType.PAWN: [], PieceType.QUEEN: [], PieceType.BISHOP: [], PieceType.KNIGHT: [],
                             PieceType.KING: [], PieceType.ROOK: []}
        self.__update_distances__()
        self.__update_pawn_moves__()
        self.__update_knight_moves__()
        self.__update_king_moves__()
        self.import_from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        self.sliding = self.piece_maps[PieceType.QUEEN] | self.piece_maps[PieceType.BISHOP] | self.piece_maps[
            PieceType.ROOK]
        self.__update_attacker__(True)
        self.__update_attacker__(False)
        self.__update_pins_and_checks__(True)

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
        if self.is_cell_empty(cell):
            return PieceType.EMPTY

        if (self.sliding & (1 << cell)) != 0:
            if (self.piece_maps[PieceType.ROOK] & (1 << cell)) != 0:
                return PieceType.ROOK
            elif (self.piece_maps[PieceType.BISHOP] & (1 << cell)) != 0:
                return PieceType.BISHOP
            else:
                return PieceType.QUEEN
        else:
            if (self.piece_maps[PieceType.PAWN] & (1 << cell)) != 0:
                return PieceType.PAWN
            elif (self.piece_maps[PieceType.KING] & (1 << cell)) != 0:
                return PieceType.KING
            else:
                return PieceType.KNIGHT

    def __update_pawn_moves__(self):
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

    def get_pawn_captures(self, cell: int, is_white: bool):
        captures = self.pawn_moves[0] if is_white else self.pawn_moves[1]
        return captures[cell]

    def get_pawn_moves(self, cell: int, is_white: bool):
        pawn_advancement = 8 if is_white else -8
        start_row = 1 if is_white else 6
        en_passant_row = 4 if is_white else 3
        board = self.black_board if is_white else self.white_board
        row = int(cell / 8)
        captures = self.get_pawn_captures(cell, is_white) & board
        forward = cell + pawn_advancement
        moves = 0
        if (forward & 0x40) == 0:
            moves = binary_ops_utils.switch_cell_bit(0, forward, True)
            forward = forward + pawn_advancement
            if (forward & 0x40) == 0:
                moves = binary_ops_utils.switch_cell_bit(moves, forward, row == start_row)
        moves = moves & (~self.board)
        if self.en_passant_ready != 0 and row == en_passant_row:
            if cell + 1 == self.en_passant_ready:
                moves = binary_ops_utils.switch_cell_bit(moves, cell + 9, True)
            elif cell - 1 == self.en_passant_ready:
                moves = binary_ops_utils.switch_cell_bit(moves, cell + 7, True)

        return moves | captures

    def __update_knight_moves__(self):
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

    def __update_king_moves__(self):
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

    def get_king_cell_moves(self, cell: int, is_white: bool):
        board = self.white_board if is_white else self.black_board
        return self.king_moves[cell] & (~board)

    def get_knight_moves(self, row: int, col: int, is_white: bool):
        cell = binary_ops_utils.translate_row_col_to_cell(row, col)
        if cell == -1 or (not self.is_type_of(cell, PieceType.KNIGHT)):
            return []
        board = self.white_board if is_white else self.black_board
        return self.knight_moves[cell] & (~board)

    def get_knight_cell_moves(self, cell: int, is_white):
        board = self.white_board if is_white else self.black_board
        return self.knight_moves[cell] & (~board)

    def __update_distances__(self):
        for i in range(8):
            for j in range(8):
                north = 7 - i
                south = i
                west = j
                east = 7 - j
                self.vertical_distances.append((east, west, north, south,
                                                min(north, west), min(south, east), min(north, east), min(south, west)))

    def get_vertical_cell_moves(self, cell: int, piece: PieceType, is_white: bool):
        # TODO: Optimize to use logical operations and masks if necessary
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
            return self.get_king_cell_moves(cell, is_white)
        elif piece == PieceType.KNIGHT:
            return self.get_knight_cell_moves(cell, is_white)
        return self.get_vertical_cell_moves(cell, piece, is_white)

    def get_moves_by_piece_(self, cell: int, is_white: bool, piece: PieceType):
        if piece == PieceType.PAWN:
            return self.get_pawn_moves(cell, is_white)
        elif piece == PieceType.KING:
            return self.get_king_cell_moves(cell, is_white)
        elif piece == PieceType.KNIGHT:
            return self.get_knight_cell_moves(cell, is_white)
        return self.get_vertical_cell_moves(cell, piece, is_white)

    def get_distances(self):
        return self.vertical_distances

    def __update_attacker__(self, is_white, piece=PieceType.EMPTY, new_cell=0):
        piece_dict = self.get_pieces_dict(is_white)
        index = 0 if is_white else 1
        self.attackers[index] = 0
        if piece == PieceType.EMPTY:
            for piece in piece_dict.keys():
                self.attackers_maps[piece][index] = 0
                for cell in piece_dict[piece]:
                    self.attackers_maps[piece][index] |= self.get_moves_by_piece_(cell, is_white, piece)
        else:
            self.attackers_maps[piece][index] = 0
            for cell in piece_dict[piece]:
                self.attackers_maps[piece][index] |= self.get_moves_by_piece_(cell, is_white, piece)
            if self.attackers_maps[PieceType.QUEEN][index] & new_cell != 0:
                self.attackers_maps[PieceType.QUEEN][index] = 0
                for cell in piece_dict[PieceType.QUEEN]:
                    self.attackers_maps[PieceType.QUEEN][index] |= self.get_moves_by_piece_(cell, is_white,
                                                                                            PieceType.QUEEN)
            if self.attackers_maps[PieceType.BISHOP][index] & new_cell != 0:
                self.attackers_maps[PieceType.BISHOP][index] = 0
                for cell in piece_dict[PieceType.BISHOP]:
                    self.attackers_maps[PieceType.BISHOP][index] |= self.get_moves_by_piece_(cell, is_white,
                                                                                             PieceType.BISHOP)
            if self.attackers_maps[PieceType.ROOK][index] & new_cell != 0:
                self.attackers_maps[PieceType.ROOK][index] = 0
                for cell in piece_dict[PieceType.ROOK]:
                    self.attackers_maps[PieceType.ROOK][index] |= self.get_moves_by_piece_(cell, is_white,
                                                                                           PieceType.ROOK)
        self.sliding_attacks = 0
        self.sliding_attacks |= self.attackers_maps[PieceType.QUEEN][index]
        self.sliding_attacks |= self.attackers_maps[PieceType.ROOK][index]
        self.sliding_attacks |= self.attackers_maps[PieceType.BISHOP][index]
        self.attackers[index] = self.attackers_maps[PieceType.PAWN][index] | self.attackers_maps[PieceType.KING][index]
        self.attackers[index] |= self.attackers_maps[PieceType.KNIGHT][index]
        self.attackers[index] |= self.sliding_attacks

    def get_attacks(self, is_white: bool):
        return self.attackers[1] if is_white else self.attackers[0]

    def __update_pins_and_checks__(self, is_white: bool):
        pieces_dict = self.get_pieces_dict(is_white)
        enemy_dict = self.get_pieces_dict(not is_white)
        king_cell = pieces_dict[PieceType.KING][0]
        index = 1 if is_white else 0
        self.pin_map = 0
        self.position_in_check = False
        self.check_map = 0
        start = 0
        end = 8
        if len(enemy_dict[PieceType.QUEEN]) == 0:
            start = 0 if len(enemy_dict[PieceType.ROOK]) != 0 else 4
            end = 8 if len(enemy_dict[PieceType.BISHOP]) != 0 else 4

        for direction_index in range(start, end):
            offset = self.directions[direction_index]
            mask = 0
            is_diagonal = (direction_index & 4) != 0
            num = self.vertical_distances[king_cell][direction_index]
            friend_ray = False
            for i in range(num):
                destination = king_cell + offset * (i + 1)
                mask |= 1 << destination
                if not self.is_cell_empty(destination):
                    if self.is_cell_colored(destination, is_white):
                        if friend_ray:
                            break
                        else:
                            friend_ray = True
                    else:
                        can_diagonal = ((1 << destination) & self.sliding != 0) and (
                            not self.is_type_of(destination, PieceType.ROOK))
                        can_vertical = ((1 << destination) & self.sliding != 0) and (
                            not self.is_type_of(destination, PieceType.BISHOP))
                        threat = (is_diagonal and can_diagonal) or ((not is_diagonal) and can_vertical)
                        if threat:
                            if friend_ray:
                                self.pin_in_position = True
                                self.pin_map |= mask
                            else:
                                self.check_map |= mask
                                self.position_in_double_check = self.position_in_check
                                self.position_in_check = True
                        break

        for cell in enemy_dict[PieceType.KNIGHT]:
            if self.knight_moves[cell] & (1 << king_cell) != 0:
                self.check_map = binary_ops_utils.switch_cell_bit(self.check_map, cell, True)
                self.position_in_double_check = self.position_in_check
                self.position_in_check = True
                return

        king_row = int(king_cell / 8)
        # we check the enemies pawns
        pawn_advancement = -1 if is_white else 1
        start_row = 6 if is_white else 1
        if (1 << king_cell) & self.attackers_maps[PieceType.PAWN][index] == 0:
            return
        for cell in enemy_dict[PieceType.PAWN]:
            pawn_row = int(cell / 8)
            if pawn_row + pawn_advancement != king_row and (pawn_row != start_row):
                continue
            if self.get_pawn_captures(cell, is_white) & (1 << king_cell) != 0:
                self.check_map = binary_ops_utils.switch_cell_bit(self.check_map, cell, True)
                self.position_in_double_check = self.position_in_check
                self.position_in_check = True
                return

    def is_pinned(self, cell: int):
        if not self.pin_in_position:
            return False

        return self.pin_map & (1 << cell) != 0

    def update_round(self, target_cell, piece: PieceType, enables_en_passant=False):
        self.en_passant_ready = target_cell if enables_en_passant else 0
        self.sliding = self.piece_maps[PieceType.QUEEN] | self.piece_maps[PieceType.BISHOP] | self.piece_maps[
            PieceType.ROOK]
        self.__update_attacker__(self.is_white, piece, target_cell)
        self.is_white = not self.is_white
        self.__update_pins_and_checks__(self.is_white)
        self.count += 1
