# cython: language_level=3
# cython: profile=True
from typing import Dict, List, Optional
import builtins

cimport binary_ops_utils
from cython cimport int, long
from mask_utils cimport Masks
from piece cimport PieceType

cdef str default_fen
default_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

cdef unsigned long long base
base = 1

cdef class Board:
    """

    This is The class that represents the game board and the values regarding it's current state.

    """

    def __cinit__(self, fen_string=default_fen):
        """ This method initiate the board to state by a fen notation.

        :param fen_string: The notation that represent the current board, the default is initial board.
        """
        self.pieces_dict = {'q': PieceType.QUEEN, 'r': PieceType.ROOK, 'b': PieceType.BISHOP, 'n': PieceType.KNIGHT,
                   'k': PieceType.KING, 'p': PieceType.PAWN}
        self.pawn_moves = []
        self.knight_moves = []
        self.king_moves = []
        self.vertical_distances = []
        self.masker = Masks()
        self.directions = [1, -1, 8, -8, 7, -7, 9, -9]
        self.castling_options = ''
        self.is_white = True
        self.en_passant_ready = 0
        self.count = 0
        self.board = 0
        self.white_board = 0
        self.black_board = 0
        self.sliding = 0
        self.sliding_attacks = 0
        self.attackers = [0, 0]
        self.pin_in_position = False
        self.attackers_maps = {PieceType.PAWN: [0, 0], PieceType.QUEEN: [0, 0], PieceType.BISHOP: [0, 0],
                               PieceType.KNIGHT: [0, 0],
                               PieceType.KING: [0, 0], PieceType.ROOK: [0, 0]}
        self.pin_map = 0
        self.check_map = 0
        self.position_in_check = False
        self.position_in_double_check = False
        self.piece_maps = {PieceType.PAWN: 0, PieceType.QUEEN: 0, PieceType.BISHOP: 0, PieceType.KNIGHT: 0,
                           PieceType.KING: 0, PieceType.ROOK: 0}
        self.threats = []
        self.black_pieces = {PieceType.PAWN: [], PieceType.QUEEN: [], PieceType.BISHOP: [], PieceType.KNIGHT: [],
                             PieceType.KING: [], PieceType.ROOK: []}
        self.white_pieces = {PieceType.PAWN: [], PieceType.QUEEN: [], PieceType.BISHOP: [], PieceType.KNIGHT: [],
                             PieceType.KING: [], PieceType.ROOK: []}
        self.__update_distances__()
        self.__update_pawn_moves__()
        self.__update_knight_moves__()
        self.__update_king_moves__()
        self.import_from_fen(fen_string)
        self.sliding = self.piece_maps[PieceType.QUEEN] | self.piece_maps[PieceType.BISHOP] | self.piece_maps[
            PieceType.ROOK]
        self.__update_attacker__(True)
        self.__update_attacker__(False)
        self.__update_pins_and_checks__(self.is_white)

    def import_from_fen(self, fen_string):
        """ This method receives a fen_string and initialize the relevant values of the board with it.

        :param fen_string: The notation that represent the state of the game with piece locations and castling options.
        """

        self.black_pieces = {PieceType.PAWN: [], PieceType.QUEEN: [], PieceType.BISHOP: [], PieceType.KNIGHT: [],
                             PieceType.KING: [], PieceType.ROOK: []}
        self.white_pieces = {PieceType.PAWN: [], PieceType.QUEEN: [], PieceType.BISHOP: [], PieceType.KNIGHT: [],
                             PieceType.KING: [], PieceType.ROOK: []}
        parts = fen_string.split()

        # In this part there is a description of the pieces in each row from the eighth rank to the first.
        rows = parts[0].split("/")
        rows.reverse()

        # The second part holds the player to play.
        self.is_white = True if parts[1].lower() == 'w' else False

        # The third part holds which castling moves are still legal.
        self.castling_options = parts[2]

        # The fourth part holds a pawn cell that can be en-passant against.
        diff = -1 if self.is_white else 1
        self.en_passant_ready = 0 if parts[3] == "-" else binary_ops_utils.translate_row_col_to_cell(
            builtins.int(parts[3][1]) + diff, ord(parts[3][0].lower()) - ord('a') + 1)

        # Read the row and update the board state.
        for i in range(8):
            j = 0
            row = rows[i]
            for letter in row:
                if letter.isdigit():
                    j += builtins.int(letter)
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

    cpdef unsigned long long get_board(self):
        """
        :return: The board bitmap, each index is 0 if the relevant cell is empty else 1
        """

        return self.board

    cpdef bint is_cell_empty(self, unsigned long cell):
        """ Returns if a certain cell is empty.

        :param cell: The cell index of the cell we check
        :return: True if the cell empty, False otherwise
        """

        return (self.board & (base << cell)) == 0

    cpdef bint is_cell_colored(self, unsigned long cell, bint is_white):
        """ This method returns if a certain cell is in specified color

        :param cell: The cell index
        :param is_white: The color we want to check, True if white False if black
        :return: True if cell is in the color of is_white
        """
        cdef unsigned long long board
        
        board = self.white_board if is_white else self.black_board
        return (board & (base << cell)) != 0

    cpdef void set_cell_piece(self, unsigned long cell, PieceType piece, bint is_white):
        """ This method set a certain cell to hold a certain piece and update the required object fields

        :param cell: The cell in which we add the piece
        :param piece: The piece type
        :param is_white: The color of the piece
        """

        self.board = binary_ops_utils.switch_cell_bit(self.board, cell, True)
        self.piece_maps[piece] = binary_ops_utils.switch_cell_bit(self.piece_maps[piece], cell, True)
        if is_white:
            self.white_pieces[piece].append(cell)
            self.white_board = binary_ops_utils.switch_cell_bit(self.white_board, cell, True)
        else:
            self.black_pieces[piece].append(cell)
            self.black_board = binary_ops_utils.switch_cell_bit(self.black_board, cell, True)

    cpdef void remove_cell_piece(self, unsigned long cell, PieceType piece, bint is_white):
        """ This method remove a piece from a certain cell and update the required object fields

        :param cell: The cell in which we remove the piece
        :param piece: The piece type
        :param is_white: The color of the piece
        """

        self.board = binary_ops_utils.switch_cell_bit(self.board, cell, False)
        self.piece_maps[piece] = binary_ops_utils.switch_cell_bit(self.piece_maps[piece], cell, False)
        if is_white:
            self.white_pieces[piece] = [c for c in self.white_pieces[piece] if c != cell]
            self.white_board = binary_ops_utils.switch_cell_bit(self.white_board, cell, False)
        else:
            self.black_pieces[piece] = [c for c in self.black_pieces[piece] if c != cell]
            self.black_board = binary_ops_utils.switch_cell_bit(self.black_board, cell, False)

    cpdef dict get_pieces_dict(self, bint is_white):
        """ This function returns the dictionary of the cells in which certain piece type is found.

        :param is_white: If we want the dict for the white pieces or not
        :return: The required dictionary
        """

        return self.white_pieces if is_white else self.black_pieces

    cpdef bint is_insufficient(self):
        """ This function returns if the board pieces are insufficient

        :return: True if the board state is insufficient for a mate, False otherwise.
        """

        if self.white_pieces[PieceType.PAWN] == [] and self.black_pieces[PieceType.PAWN] == []:
            if len(self.white_pieces[PieceType.ROOK] + self.white_pieces[PieceType.QUEEN]) == 0 and len(
                    self.white_pieces[PieceType.BISHOP] + self.white_pieces[PieceType.KNIGHT]) <= 1:
                return len(self.black_pieces[PieceType.ROOK] + self.black_pieces[PieceType.QUEEN]) == 0 and len(
                    self.black_pieces[PieceType.BISHOP] + self.black_pieces[PieceType.KNIGHT]) <= 1
        return False

    cpdef bint is_type_of(self, unsigned long cell, PieceType piece):
        """ This function return if the PieceType of the a certain cell in the board is the piece it received.

        :param cell: The cell index of the cell we check
        :param piece: The PieceType which we compare to the cell type
        :return: True if the cell PieceType is piece, False otherwise
        """

        return (self.piece_maps[piece] & (base << cell)) != 0

    cpdef PieceType get_cell_type(self, unsigned long cell):
        """ Returns The PieceType of certain cell

        :param cell: The cell index
        :return: The cell's PieceType
        """

        if self.is_cell_empty(cell):
            return PieceType.EMPTY

        # I created a bit map for the sliding pieces as optimization for the search.
        if (self.sliding & (base << cell)) != 0:
            if (self.piece_maps[PieceType.ROOK] & (base << cell)) != 0:
                return PieceType.ROOK
            elif (self.piece_maps[PieceType.BISHOP] & (base << cell)) != 0:
                return PieceType.BISHOP
            else:
                return PieceType.QUEEN
        else:
            if (self.piece_maps[PieceType.PAWN] & (base << cell)) != 0:
                return PieceType.PAWN
            elif (self.piece_maps[PieceType.KING] & (base << cell)) != 0:
                return PieceType.KING
            else:
                return PieceType.KNIGHT

    def __update_pawn_moves__(self) -> None:
        """
        This function creates an array of all the possible capture moves for a pawn based on cell index.
        This function is made for internal use.
        """

        white_moves = []
        black_moves = []
        for i in range(8):
            for j in range(8):
                white_val = 0
                black_val = 0
                # Here we filter the moves that are outside of the board.
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

    cpdef bint __is_safe_en_passant__(self, unsigned long pawn_cell, unsigned long enemy_cell, bint is_white):
        cdef long king_cell, king_col, king_row, pawn_col, pawn_row, checked_cell
        cdef long start_col, end_col, start_cell, end_cell
        cdef int direction
        cdef bint threat, block, is_threat

        king_cell = self.get_pieces_dict(is_white)[PieceType.KING][0]
        king_row, king_col = binary_ops_utils.translate_cell_to_row_col(king_cell)
        pawn_row, pawn_col = binary_ops_utils.translate_cell_to_row_col(pawn_cell)
        if king_col == pawn_col:
            direction = 8 if king_row < pawn_row else -8
            checked_cell = king_cell + direction
            threat = False
            block = False
            while checked_cell & 0x40 == 0:
                if self.is_cell_colored(checked_cell, is_white):
                    if checked_cell != pawn_cell:
                        # There is a blocking piece
                        block = True

                elif self.is_cell_colored(checked_cell, not is_white):
                    is_threat = ((base << checked_cell) & self.sliding != 0) and (
                        not self.is_type_of(checked_cell, PieceType.BISHOP))

                    if is_threat:
                        if not block:
                            return False

                    block = True
                checked_cell = checked_cell + direction

            return not threat

        if king_row == pawn_row:
            direction = 1 if king_col < pawn_col else -1
            start_col = king_col + 1 if king_col < pawn_col else -1
            end_col = 8 if king_col < pawn_col else king_col
            start_cell = 8 * king_row + start_col
            end_cell = 8 * king_row + end_col
            block = False
            if direction < 0:
                start_cell, end_cell = end_cell, start_cell

            for checked_cell in range(start_cell, end_cell, direction):
                if self.is_cell_colored(checked_cell, is_white):
                    if checked_cell != pawn_cell and checked_cell != king_cell:
                        # There is a blocking piece
                        block = True

                elif self.is_cell_colored(checked_cell, not is_white):
                    if checked_cell == enemy_cell:
                        continue

                    is_threat = ((base << checked_cell) & self.sliding != 0) and (
                        not self.is_type_of(checked_cell, PieceType.BISHOP))

                    if is_threat:
                        if not block:
                            return False

                    block = True
            return True

        return True

    cpdef unsigned long long get_pawn_captures(self, unsigned long cell, bint is_white):
        """ Returns the possible pawn capture moves for a certain cell based on pawn color

        :param cell: The cell index
        :param is_white: The color of the pawn
        :return: The possible theoretical captures in a bitmap format
        """
        cdef list captures

        captures = self.pawn_moves[0] if is_white else self.pawn_moves[1]
        return captures[cell]

    cpdef unsigned long long get_pawn_moves(self, unsigned long cell, bint is_white):
        """ This function returns a bitmap of all the legal pawn moves on the board

        :param cell: The cell index
        :param is_white: The color of the pawn
        :return: The bitmap of the pseudo legal pawn moves from a certain cell.
        """
        cdef long pawn_advancement, start_row, en_passant_row, row, forward
        cdef unsigned long long board, captures, moves

        pawn_advancement = 8 if is_white else -8
        start_row = 1 if is_white else 6
        en_passant_row = 4 if is_white else 3
        board = self.black_board if is_white else self.white_board
        row = <int>(cell / 8)
        captures = self.get_pawn_captures(cell, is_white) & board

        forward = cell + pawn_advancement
        moves = 0
        # The and to 0x40 is because if the row is below 0 or 64 and above the bit that represent 0x40 would turn on.
        if (forward & 0x40) == 0:
            moves = binary_ops_utils.switch_cell_bit(0, forward, True)
            forward = forward + pawn_advancement
            moves = moves & (~self.board)
            if (forward & 0x40) == 0:
                moves = binary_ops_utils.switch_cell_bit(moves, forward, row == start_row and (moves != 0))
                moves = moves & (~self.board)

        if self.en_passant_ready != 0 and row == en_passant_row:
            if cell + 1 == self.en_passant_ready:
                pawn_advancement = 9 if is_white else -7
                if self.__is_safe_en_passant__(cell, cell + 1, is_white):
                    moves = binary_ops_utils.switch_cell_bit(moves, cell + pawn_advancement, True)
            elif cell - 1 == self.en_passant_ready:
                pawn_advancement = 7 if is_white else -9
                if self.__is_safe_en_passant__(cell, cell - 1, is_white):
                    moves = binary_ops_utils.switch_cell_bit(moves, cell + pawn_advancement, True)

        return moves | captures

    def __update_knight_moves__(self):
        """
        This function creates an array of all the possible moves for a knight based on cell index.
        This function is made for internal use
        """

        moves = [(2, 1), (2, -1), (-2, 1), (-2, -1),
                 (1, 2), (-1, 2), (1, -2), (-1, -2)]
        for i in range(8):
            for j in range(8):
                val = 0
                options = []
                for move in moves:
                    # filter illegal moves.
                    if binary_ops_utils.translate_row_col_to_cell(move[0] + i + 1, move[1] + j + 1) != -1:
                        options.append((move[0] + i, move[1] + j))

                for option in options:
                    val = binary_ops_utils.switch_cell_bit(val, option[0] * 8 + option[1], True)
                self.knight_moves.append(val)

    def __update_king_moves__(self) -> None:
        """
        This function creates an array of all the possible moves for a king based on cell index.
        This function is made for internal use
        """
        moves = [(0, 1), (0, -1), (1, 1), (-1, -1),
                 (1, -1), (-1, 1), (1, 0), (-1, 0)]
        for i in range(8):
            for j in range(8):
                val = 0
                options = []
                for move in moves:
                    # filter illegal moves.
                    if binary_ops_utils.translate_row_col_to_cell(move[0] + i + 1, move[1] + j + 1) != -1:
                        options.append((move[0] + i, move[1] + j))

                for option in options:
                    val = binary_ops_utils.switch_cell_bit(val, option[0] * 8 + option[1], True)
                self.king_moves.append(val)

    cpdef unsigned long long get_king_cell_moves(self, unsigned long cell, bint is_white):
        """ Returns pseudo-legal move for a king at a certain cell.

        :param cell: The king's cell
        :param is_white: The king's color
        :return: The bitmap of his pseudo-legal moves
        """
        cdef unsigned long long board

        board = self.white_board if is_white else self.black_board
        return self.king_moves[cell] & (~board)

    cpdef unsigned long long get_knight_cell_moves(self, unsigned long cell, bint is_white):
        """ This returns the pseudo legal knight moves

        :param cell: The knight's cell
        :param is_white: The knight's color
        :return: Bitmap for the knight pseudo legal moves, 1 indicate legal 0 indicate non legal
        """
        cdef unsigned long long board

        board = self.white_board if is_white else self.black_board
        return self.knight_moves[cell] & (~board)

    def __update_distances__(self) -> None:
        """
        This function creates an array of all the possible moves for a vertical line based on cell index.
        This function is made for internal use
        """
        for i in range(8):
            for j in range(8):
                north = 7 - i
                south = i
                west = j
                east = 7 - j
                self.vertical_distances.append((east, west, north, south,
                                                min(north, west), min(south, east), min(north, east), min(south, west)))

    cpdef unsigned long long get_vertical_cell_moves(self, unsigned long cell, PieceType piece, bint is_white, bint for_attacks=False):
        """ This function returns all pseudo-legal vertical move by cell, piece type and color

        :param cell: The piece cell
        :param piece: The piece type
        :param is_white: The piece color
        :param for_attacks: Flag that is used when checking if a piece is supported by another piece.
        :return: Bitmap of pseudo-legal moves
        """
        cdef unsigned long long result 

        result = 0
        if piece == PieceType.ROOK:
            result = binary_ops_utils.get_rook_moves(self.board, cell, self.masker)
        elif piece == PieceType.BISHOP:
            result = binary_ops_utils.get_bishop_moves(self.board, cell, self.masker)
        elif piece == PieceType.QUEEN:
            result = binary_ops_utils.get_queen_moves(self.board, cell, self.masker)
        board = self.white_board if is_white else self.black_board
        return (result ^ (base << cell)) if for_attacks else result & (~board)

    cpdef unsigned long long get_moves_by_piece(self, unsigned long cell, bint is_white, PieceType piece, bint for_attacks=False):
        """ Returns all pseudo-legal moves from a cell for a certain piece type and color.

        :param cell: The cell's index
        :param is_white: The cell's color
        :param piece: The piece type
        :param for_attacks: flag for whether this is used for checking king's move
        :return: Bitmap of all pseudo-legal moves
        """

        if piece == PieceType.PAWN:
            return self.get_pawn_captures(cell, is_white) if for_attacks else self.get_pawn_moves(cell, is_white)
        elif piece == PieceType.KING:
            return self.king_moves[cell] if for_attacks else self.get_king_cell_moves(cell, is_white)
        elif piece == PieceType.KNIGHT:
            return self.knight_moves[cell] if for_attacks else self.get_knight_cell_moves(cell, is_white)
        return self.get_vertical_cell_moves(cell, piece, is_white, for_attacks)

    cpdef unsigned long long get_moves_by_cell(self, unsigned long cell, bint is_white, bint for_attacks=False):
        """ Returns all pseudo-legal moves from a cell for a certain color.

        :param cell: The cell's index
        :param is_white: The cell's color
        :param for_attacks: flag for whether this is used for checking king's move
        :return: Bitmap of all pseudo-legal moves
        """
        cdef PieceType piece

        piece = self.get_cell_type(cell)
        if self.is_cell_empty(cell):
            return 0

        return self.get_moves_by_piece(cell, is_white, piece, for_attacks)

    cpdef void __update_attacker__(self, bint is_white):
        """ This is a method to update the attacker's bitmaps and is for internal use only.

        :param is_white: The color which we update
        :param piece: Optional param, used for optimization where we update impacted maps, currently not in use.
        """
        cdef dict piece_dict
        cdef int index
        cdef unsigned long long temp

        piece_dict = self.get_pieces_dict(is_white)
        index = 0 if is_white else 1
        self.attackers[index] = 0

        # Update all maps.
        for piece in piece_dict.keys():
            temp = 0            
            for cell in piece_dict[piece]:
                temp |= self.get_moves_by_piece(cell, is_white, piece, True)
            self.attackers_maps[piece][index] = temp


        # Update board state
        temp = 0
        temp |= self.attackers_maps[PieceType.QUEEN][index]
        temp |= self.attackers_maps[PieceType.ROOK][index]
        temp |= self.attackers_maps[PieceType.BISHOP][index]
        self.sliding_attacks = temp

        temp = 0
        temp = self.attackers_maps[PieceType.PAWN][index] | self.attackers_maps[PieceType.KING][index]
        temp |= self.attackers_maps[PieceType.KNIGHT][index]
        self.attackers[index] = self.sliding_attacks | temp

    cpdef unsigned long long get_attacks(self, bint is_white):
        """ Returns the bitmap of the attacks on certain player.

        :param is_white: Player's color
        :return: The attack bitmap
        """
        return self.attackers[1] if is_white else self.attackers[0]

    cpdef void __update_pins_and_checks__(self, bint is_white):
        """ This is function for internal use to update the attacks, pin, threats and checks on the king

        :param is_white: The king's color
        """
        cdef dict pieces_dict, enemy_dict
        cdef unsigned long king_cell, destination, tmp, cell
        cdef int index, start, end, direction_index, offset, num, i, pawn_advancement, king_row, pawn_row
        cdef unsigned long long mask
        cdef bint is_diagonal, friend_ray, can_diagonal, can_vertical, threat

        pieces_dict = self.get_pieces_dict(is_white)
        enemy_dict = self.get_pieces_dict(not is_white)
        king_cell = pieces_dict[PieceType.KING][0]
        index = 1 if is_white else 0
        self.pin_map = 0
        self.pin_in_position = False
        self.position_in_check = False
        self.position_in_double_check = False
        self.check_map = 0
        self.threats = []
        start = 0
        end = 8
        if len(enemy_dict[PieceType.QUEEN]) == 0:
            start = 0 if len(enemy_dict[PieceType.ROOK]) != 0 else 4
            end = 8 if len(enemy_dict[PieceType.BISHOP]) != 0 else 4

        # Check threats from sliding pieces in each direction.
        for direction_index in range(start, end):
            offset = self.directions[direction_index]
            mask = 0
            is_diagonal = (direction_index & 4) != 0
            num = self.vertical_distances[king_cell][direction_index]
            friend_ray = False
            for i in range(num):
                destination = king_cell + offset * (i + 1)
                mask |= base << destination
                if not self.is_cell_empty(destination):
                    if self.is_cell_colored(destination, is_white):
                        if friend_ray:
                            break
                        else:
                            friend_ray = True
                    else:
                        can_diagonal = ((base << destination) & self.sliding != 0) and (
                            not self.is_type_of(destination, PieceType.ROOK))
                        can_vertical = ((base << destination) & self.sliding != 0) and (
                            not self.is_type_of(destination, PieceType.BISHOP))
                        threat = (is_diagonal and can_diagonal) or ((not is_diagonal) and can_vertical)
                        if threat:
                            if friend_ray:
                                self.pin_in_position = True
                                self.pin_map |= mask
                            else:
                                tmp = king_cell - offset
                                if tmp >= 0:
                                    index = 1 if is_white else 0
                                    self.attackers[index] |= (base << tmp)
                                self.check_map |= mask
                                self.position_in_double_check = self.position_in_check
                                self.position_in_check = True
                                self.threats.append(destination)
                        break

        # Check attacks from enemy knights.
        for cell in enemy_dict[PieceType.KNIGHT]:
            if self.knight_moves[cell] & (base << king_cell) != 0:
                self.check_map = binary_ops_utils.switch_cell_bit(self.check_map, cell, True)
                self.position_in_double_check = self.position_in_check
                self.position_in_check = True
                self.threats.append(cell)
                return

        king_row = <int>(king_cell / 8)
        # We check the enemies pawns.
        pawn_advancement = -1 if is_white else 1
        if (base << king_cell) & self.attackers_maps[PieceType.PAWN][index] == 0:
            return
        for cell in enemy_dict[PieceType.PAWN]:
            pawn_row = <int>(cell / 8)
            if pawn_row + pawn_advancement != king_row:
                continue
            if self.get_pawn_captures(cell, not is_white) & (base << king_cell) != 0:
                self.check_map = binary_ops_utils.switch_cell_bit(self.check_map, cell, True)
                self.position_in_double_check = self.position_in_check
                self.position_in_check = True
                self.threats.append(cell)
                return

    cpdef bint is_pinned(self, unsigned long cell):
        """ This returns whether a cell is pinned by the opponent.

        :param cell: The cell index
        :return: True if the piece on said cell is pinned.
        """

        if not self.pin_in_position:
            return False

        return self.pin_map & (base << cell) != 0

    cpdef void update_round(self, unsigned long target_cell, PieceType piece, bint enables_en_passant=False):
        """ This method updates the board state after a move.

        :param target_cell: The move's destination cell
        :param piece: The piece that were moved
        :param enables_en_passant: Flag that says whether it allows en-passant on the next move
        """

        self.en_passant_ready = target_cell if enables_en_passant else 0
        self.sliding = self.piece_maps[PieceType.QUEEN] | self.piece_maps[PieceType.BISHOP] | self.piece_maps[
            PieceType.ROOK]
        self.__update_attacker__(True)
        self.__update_attacker__(False)
        self.is_white = not self.is_white
        self.__update_pins_and_checks__(self.is_white)

        if piece == PieceType.PAWN:
            self.count = 0
        self.count += 1
