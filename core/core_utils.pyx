# cython: language_level=3
from typing import List

cimport binary_ops_utils
from board cimport Board
from .chess_exceptions import NonLegal, KingUnderCheck
from piece cimport PieceType

cdef unsigned long long base
base = 1

cdef unsigned long abs(long num):
    if num > 0:
        return num
    return -num
cdef class Move:
    """
    This class represent a move in the game with origin, target, castling and promotion data
    """

    def __cinit__(self, cell: int, tar: int):
        """ Initialize to a standard move

        :param cell: The origin cell index
        :param tar: The target cel index
        """

        self.cell = cell
        self.target = tar
        self.castle = False
        self.is_king_side = False
        self.is_en_passant = False
        self.promotion = PieceType.EMPTY
        self.enemy_type = PieceType.EMPTY
        self.enemy_cell = 0
        self.prev_en_passant = 0
        self.prev_castling = u''

    cpdef void set_castle(self, bint is_king_side):
        """ This defines the move to be a castling move

        :param is_king_side: Whether to castling is to the king side
        """
        self.castle = True
        self.is_king_side = is_king_side

    cpdef void set_promotion(self, PieceType piece):
        """ Define the move as a promotion move and set the target piece

        :param piece: The piece which it will promote to
        """
        self.promotion = piece


cpdef bint is_pseudo_legal(Board board, Move move):
    """ Return whether a move is pseudo legal on a board

    :param board: The board on which we check
    :param move: The move we validate
    :return: Whether the move is pseudo legal or not
    """
    cdef unsigned long long moves

    moves = board.get_moves_by_cell(move.cell, board.is_white)
    return moves & binary_ops_utils.switch_cell_bit(0, move.target, True) != 0


cpdef bint is_threatened(Board board, bint is_white, unsigned long cell):
    """ Returns if a cell is threatened

    :param board: The board on which we check
    :param is_white: If it the white player
    :param cell: The cell we check
    :return: If the cell is in the attacked cells of the opponent
    """
    return binary_ops_utils.switch_cell_bit(0, cell, True) & board.get_attacks(is_white) != 0


cpdef list get_all_legal_moves(Board board, unsigned long cell, PieceType piece, bint is_white):
    """ Returns all the legal move from a certain cell with a certain PieceType

    :param board: The board we use
    :param cell: The cell we check
    :param piece: The piece type of the cell
    :param is_white: Whether it is the turn of the white player or not
    :return: All legal moves in the board position as a list of moves
    """
    cdef list moves, targets
    cdef Move move
    cdef unsigned long target

    if board.is_cell_empty(cell) or board.is_cell_colored(cell, not is_white):
        return []

    moves = []
    targets = binary_ops_utils.get_turned_bits(board.get_moves_by_cell(cell, is_white))

    for target in targets:
        move = Move(cell, target)
        if condition(board, move, piece, is_white):
            if piece == PieceType.PAWN:
                promotion_rank = 7 if board.is_white else 0
                if <int>(target / 8) == promotion_rank:
                    moves += get_promotion_moves(move)
                    continue
            moves.append(move)

    if piece == PieceType.KING:
        moves += get_castle_moves(board, board.is_cell_colored(cell, True))

    return moves


cpdef bint condition(Board board, Move move, PieceType piece, bint is_white):
    """ Returns if a move on the board for a certain piece is legal/

    :param board: The board we check
    :param move: The move we validate
    :param piece: The move's origin cell PieceType
    :param is_white: Whether it is a move of the white player
    :return: If the move is legal
    """
    cdef unsigned long cell, king_cell, en_capture
    cdef int step, direction

    if piece == PieceType.EMPTY:
        return False

    if board.position_in_double_check and piece != PieceType.KING:
        return False

    if piece == PieceType.KING and (board.get_attacks(is_white) & (base << move.target) != 0):
        return False

    cell = move.cell
    king_cell = board.get_pieces_dict(is_white)[<int>PieceType.KING][0]
    step = binary_ops_utils.get_direction(move.target, king_cell)

    if board.position_in_check:
        # The king escapes to safety
        if piece == PieceType.KING:
            return board.get_attacks(is_white) & (base << move.target) == 0

        # The move blocks the attack and isn't pinned
        if (base << move.target) & board.check_map != 0 and (not board.is_pinned(cell)):
            return True

        # check for en_passant help
        if piece == PieceType.PAWN:
            direction = -8 if is_white else 8
            en_capture = move.target + direction
            if en_capture == board.en_passant_ready:
                return (base << en_capture) & board.check_map != 0 and (not board.is_pinned(cell))
        return False

    if not board.is_pinned(cell):
        return True

    # Check if pinned piece stays on it's ray
    return abs(binary_ops_utils.get_direction(move.cell, king_cell)) == abs(step)


cpdef list get_threats(Board board):
    """ Returns all the threats to the current player's king

    :param board: The board of the position
    :return: List of the cell indexes of pieces which threatens the king
    """

    return board.threats


cpdef bint is_under_check(Board board):
    """ Return if there is a check

    :param board: The board of the position
    :return: True if the current player is under check
    """
    return board.position_in_check


cpdef bint is_mate(Board board, bint is_white):
    """ Return if the current player is under mate.

    :param board: The board of the position
    :param is_white: Is the current player the white player
    :return: True if it is a mate for the opponent
    """
    cdef list[6] pieces_dict
    cdef unsigned long king_cell, cell
    cdef PieceType piece

    pieces_dict = board.get_pieces_dict(is_white)
    king_cell = pieces_dict[<int>PieceType.KING][0]
    if board.position_in_check:
        if not get_all_legal_moves(board, king_cell, PieceType.KING, is_white):
            if board.position_in_double_check:
                return True
            for piece in board.pieces_dict.values():
                for cell in pieces_dict[piece]:
                    if get_all_legal_moves(board, cell, piece, is_white):
                        return False
            return True
    return False


cpdef bint can_castle(Board board, bint is_white, Move move):
    """ This method validates a castling move on a certain board

    :param board: The board on which we validate the move
    :param is_white: Whether the current player is white
    :param move: The move which is validated
    :return: True if the move is a legal castling move
    """
    cdef unicode option
    cdef long direction, row, path
    cdef bint not_threatened, valid

    if move.castle is False:
        return False
    if is_under_check(board):
        return False

    option = u'k' if move.is_king_side else u'q'
    direction = 1 if move.is_king_side else -1

    row = 1 if is_white else 8
    path = binary_ops_utils.translate_row_col_to_cell(row, 5 + direction)
    not_threatened = not (is_threatened(board, is_white, path)) and (base << path) & board.get_board() == 0

    path = binary_ops_utils.translate_row_col_to_cell(row, 5 + 2 * direction)
    not_threatened = not (
        is_threatened(board, is_white,
                      binary_ops_utils.translate_row_col_to_cell(row, 5 + 2 * direction))) and not_threatened
    valid = (base << path) & board.get_board() == 0 and not_threatened

    if not move.is_king_side:
        valid = valid and (base << binary_ops_utils.translate_row_col_to_cell(row, 2)) & board.get_board() == 0

    if is_white:
        return valid and (option.upper() in board.castling_options)

    return option in board.castling_options and valid


cpdef void castle(Board board, bint is_white, Move move, bint valid=False):
    """ This method perform a castling move on a board

    :param board: The board being used
    :param is_white: The color of the player
    :param move: The castling move
    :param valid: Flag that says if the move was validated beforehand
    """
    cdef long row, col, side
    cdef unsigned long king_cell, rook_cell

    if move.castle is False:
        raise NonLegal()
    if (not valid) and is_under_check(board):
        raise KingUnderCheck()

    if not can_castle(board, is_white, move):
        raise NonLegal()

    row = 1 if is_white else 8
    col = 8 if move.is_king_side else 1
    side = -1 if move.is_king_side else 1
    king_cell = board.get_pieces_dict(is_white)[<int>PieceType.KING][0]
    rook_cell = binary_ops_utils.translate_row_col_to_cell(row, col)

    board.remove_cell_piece(king_cell, PieceType.KING, is_white)
    board.remove_cell_piece(rook_cell, PieceType.ROOK, is_white)

    if is_white:
        board.castling_options = ''.join([c for c in board.castling_options if c.islower()])
    else:
        board.castling_options = ''.join([c for c in board.castling_options if c.isupper()])
    board.set_cell_piece(move.target, PieceType.KING, is_white)
    board.set_cell_piece(move.target + side, PieceType.ROOK, is_white)
    board.update_round(move.target, PieceType.KING, False)


cpdef void promote(Board board, Move move):
    """ Perform the promotion of the piece by switching the PieceType of the cell

    :param board: The board being used
    :param move: The promotion move
    """
    cdef int promotion_rank

    if move.promotion == PieceType.EMPTY:
        raise NonLegal()

    promotion_rank = 7 if board.is_white else 0
    if <int>(move.target / 8) != promotion_rank:
        raise NonLegal()

    board.remove_cell_piece(move.cell, PieceType.PAWN, board.is_white)
    board.set_cell_piece(move.cell, move.promotion, board.is_white)


cpdef void make_move(Board board, Move move, bint valid=True):
    """ Perform a move on the board and updates the required fields

    :param board: The board
    :param move: The move being performed
    :param valid: Flag that determine whether the move was validated
    """
    cdef PieceType piece, target_type
    cdef bint enable_en_passant
    cdef long diff, side

    piece = board.get_cell_type(move.cell)
    target_type = board.get_cell_type(move.target)
    fill_undo_info(board, move, target_type)
    enable_en_passant = False
    if move.castle:
        castle(board, board.is_white, move)
        return

    if move.promotion != PieceType.EMPTY and piece == PieceType.PAWN:
        promote(board, move)
        piece = move.promotion

    if not valid:
        if not condition(board, move, piece, board.is_white):
            raise NonLegal()

    # Update the target cell piece if exist
    if target_type != PieceType.EMPTY:
        board.count = 0
        board.remove_cell_piece(move.target, target_type, not board.is_white)
        if target_type == PieceType.ROOK:
            update_castling_option(move.target, board, not board.is_white)
        move.enemy_cell = move.target

    if piece == PieceType.PAWN:
        diff = abs(move.cell - move.target)
        # If move 2 rows it can be subject to en passant
        if diff == 16:
            enable_en_passant = True

        # Check if en Passant
        if target_type == PieceType.EMPTY and (abs(move.cell - move.target) % 8 != 0):
            side = 1 if (move.cell % 8) < (move.target % 8) else -1
            board.remove_cell_piece(move.cell + side, PieceType.PAWN, not board.is_white)
            move.enemy_cell = move.cell + side
            move.enemy_type = PieceType.PAWN

    # Update castling information
    elif piece == PieceType.KING:
        if board.is_white:
            board.castling_options = ''.join([c for c in board.castling_options if c.islower()])
        else:
            board.castling_options = ''.join([c for c in board.castling_options if c.isupper()])

    elif piece == PieceType.ROOK:
        update_castling_option(move.cell, board, board.is_white)

    # Move the origin piece to the target and update the board
    board.remove_cell_piece(move.cell, piece, board.is_white)
    board.set_cell_piece(move.target, piece, board.is_white)
    board.update_round(move.target, piece, enable_en_passant)


cpdef list get_castle_moves(Board board, bint is_white):
    """ This method generate all possible castling moves for a player from certain position

    :param board: The position we use
    :param is_white: If the player is white
    :return: A list of possible castling moves
    """
    cdef list moves
    cdef unsigned long king_cell
    cdef int row
    cdef Move move_1, move_2

    moves = []
    row = 1 if is_white else 8
    king_cell = board.get_pieces_dict(is_white)[<int>PieceType.KING][0]
    move_1 = Move(king_cell, binary_ops_utils.translate_row_col_to_cell(row, 7))
    move_1.set_castle(True)
    if can_castle(board, is_white, move_1):
        moves.append(move_1)
    move_2 = Move(king_cell, binary_ops_utils.translate_row_col_to_cell(row, 3))
    move_2.set_castle(False)
    if can_castle(board, is_white, move_2):
        moves.append(move_2)
    return moves


cpdef list get_promotion_moves(Move move):
    """ Returns a list of all legal promotion cases of a promotion move

    :param move: The promotion move
    :return: A list of all the possible promotions corresponding to the move
    """
    cdef list result
    cdef Move tmp 
    cdef PieceType[4] relevant_pieces
    cdef PieceType piece

    result = []
    relevant_pieces = [PieceType.QUEEN, PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP]
    for piece in relevant_pieces:
        tmp = Move(move.cell, move.target)
        tmp.set_promotion(piece)
        result.append(tmp)
    return result


cpdef bint check_stalemate(Board board):
    """ This method returns if the board is in stalemate case, note: I haven't considered all the stalemate rules

    :param board: The position we check
    :return: If the position is in stalemate
    """
    if board.count >= 50:
        return True

    return board.is_insufficient()


cpdef void fill_undo_info(Board board, Move move, PieceType enemy_type):
    """ This method fills information about the changes the move performed on the board.

    :param board: The game board
    :param move: the move being performed
    :param enemy_type: The type of the cell we move into
    """
    move.prev_castling = board.castling_options
    move.prev_en_passant = board.en_passant_ready
    move.enemy_type = enemy_type


cpdef void update_castling_option(unsigned long rook_cell, Board board, bint is_white):
    """ This method updates the castling options after change in the position of the rooks.

    :param rook_cell: The index of the rook's cell
    :param board: The gameboard
    :param is_white: The color of the rook
    """
    cdef unsigned long rook_col, rook_row

    rook_row, rook_col = binary_ops_utils.translate_cell_to_row_col(rook_cell)
    if is_white:
        if rook_row == 0:
            if rook_col == 0:
                board.castling_options = ''.join([c for c in board.castling_options if c != u'Q'])
            elif rook_col == 7:
                board.castling_options = ''.join([c for c in board.castling_options if c != u'K'])
    else:
        if rook_row == 7:
            if rook_col == 0:
                board.castling_options = ''.join([c for c in board.castling_options if c != u'q'])
            elif rook_col == 7:
                board.castling_options = ''.join([c for c in board.castling_options if c != u'k'])


cpdef void undo_move(Board board, Move move):
    """ This method restores the board state to before the move which was performed

    :param board: The gameboard
    :param move: The last move performed on the board
    """
    cdef int start_row, king_col, king_curr_col, rook_position
    cdef bint color
    cdef long rook_origin, rook_target, king_cell, king_target
    cdef PieceType origin_piece

    board.castling_options = move.prev_castling

    if move.castle:
        start_row = 8 if board.is_white else 1
        king_col = 5
        king_curr_col = 7 if move.is_king_side else 3
        rook_position = 6 if move.is_king_side else 4
        rook_target = 8 if move.is_king_side else 1
        color = not board.is_white
        rook_origin = binary_ops_utils.translate_row_col_to_cell(start_row, rook_position)
        rook_target = binary_ops_utils.translate_row_col_to_cell(start_row, rook_target)
        king_cell = binary_ops_utils.translate_row_col_to_cell(start_row, king_curr_col)
        king_target = binary_ops_utils.translate_row_col_to_cell(start_row, king_col)
        board.remove_cell_piece(rook_origin, PieceType.ROOK, color)
        board.remove_cell_piece(king_cell, PieceType.KING, color)
        board.set_cell_piece(king_target, PieceType.KING, color)
        board.set_cell_piece(rook_target, PieceType.ROOK, color)
        board.update_round(move.target, PieceType.KING, False)
        return

    origin_piece = board.get_cell_type(move.target)

    if move.promotion != PieceType.EMPTY:
        board.remove_cell_piece(move.target, move.promotion, not board.is_white)
        board.set_cell_piece(move.target, PieceType.PAWN, not board.is_white)
        origin_piece = PieceType.PAWN

    board.remove_cell_piece(move.target, origin_piece, not board.is_white)
    board.set_cell_piece(move.cell, origin_piece, not board.is_white)
    if move.enemy_type != PieceType.EMPTY:
        board.set_cell_piece(move.enemy_cell, move.enemy_type, board.is_white)
    board.update_round(move.enemy_cell, move.enemy_type)
    board.en_passant_ready = move.prev_en_passant
