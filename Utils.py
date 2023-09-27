from typing import List

import binary_ops_utils
from board import Board
from chess_exceptions import NonLegal, KingUnderCheck
from piece import PieceType


class Move:
    """
    This class represent a move in the game with origin, target, castling and promotion data
    """
    # cell and target are cell index
    cell: int
    target: int
    castle: bool
    is_king_side: bool
    promotion: PieceType
    enemy_type: PieceType
    enemy_cell: int
    prev_castling: str
    prev_en_passant: int

    def __init__(self, cell: int, tar: int):
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
        self.prev_castling = ''

    def set_castle(self, is_king_side: bool) -> None:
        """ This defines the move to be a castling move

        :param is_king_side: Whether to castling is to the king side
        """
        self.castle = True
        self.is_king_side = is_king_side

    def set_promotion(self, piece: PieceType) -> None:
        """ Define the move as a promotion move and set the target piece

        :param piece: The piece which it will promote to
        """
        self.promotion = piece


def is_pseudo_legal(board: Board, move: Move) -> bool:
    """ Return whether a move is pseudo legal on a board

    :param board: The board on which we check
    :param move: The move we validate
    :return: Whether the move is pseudo legal or not
    """
    moves = board.get_moves_by_cell(move.cell, board.is_white)
    return moves & binary_ops_utils.switch_cell_bit(0, move.target, True) != 0


def is_threatened(board: Board, is_white: bool, cell: int) -> bool:
    """ Returns if a cell is threatened

    :param board: The board on which we check
    :param is_white: If it the white player
    :param cell: The cell we check
    :return: If the cell is in the attacked cells of the opponent
    """
    return binary_ops_utils.switch_cell_bit(0, cell, True) & board.get_attacks(is_white) != 0


def get_all_legal_moves(board: Board, cell: int, piece: PieceType, is_white: bool) -> List[Move]:
    """ Returns all the legal move from a certain cell with a certain PieceType

    :param board: The board we use
    :param cell: The cell we check
    :param piece: The piece type of the cell
    :param is_white: Whether it is the turn of the white player or not
    :return: All legal moves in the board position as a list of moves
    """
    if board.is_cell_empty(cell) or board.is_cell_colored(cell, not is_white):
        return []

    moves = []
    targets = binary_ops_utils.get_turned_bits(board.get_moves_by_cell(cell, is_white))

    for target in targets:
        move = Move(cell, target)
        if condition(board, move, piece, is_white):
            if piece == PieceType.PAWN:
                promotion_rank = 7 if board.is_white else 0
                if int(target / 8) == promotion_rank:
                    moves += get_promotion_moves(move)
                    continue
            moves.append(move)

    if piece == PieceType.KING:
        moves += get_castle_moves(board, board.is_cell_colored(cell, True))

    return moves


def condition(board: Board, move: Move, piece: PieceType, is_white: bool) -> bool:
    """ Returns if a move on the board for a certain piece is legal/

    :param board: The board we check
    :param move: The move we validate
    :param piece: The move's origin cell PieceType
    :param is_white: Whether it is a move of the white player
    :return: If the move is legal
    """

    if piece == PieceType.EMPTY:
        return False

    if board.position_in_double_check and piece != PieceType.KING:
        return False

    if piece == PieceType.KING and (board.get_attacks(is_white) & (1 << move.target) != 0):
        return False

    cell = move.cell
    king_cell = board.get_pieces_dict(is_white)[PieceType.KING][0]
    step = binary_ops_utils.get_direction(move.target, king_cell)

    if board.position_in_check:
        # The king escapes to safety
        if piece == PieceType.KING:
            return board.get_attacks(is_white) & (1 << move.target) == 0

        # The move blocks the attack and isn't pinned
        if (1 << move.target) & board.check_map != 0 and (not board.is_pinned(cell)):
            return True

        return False

    if not board.is_pinned(cell):
        return True

    # Check if pinned piece stays on it's ray
    return abs(binary_ops_utils.get_direction(move.cell, king_cell)) == abs(step)


def get_threats(board: Board):
    """ Returns all the threats to the current player's king

    :param board: The board of the position
    :return: List of the cell indexes of pieces which threatens the king
    """

    return board.threats


def is_under_check(board: Board):
    """ Return if there is a check

    :param board: The board of the position
    :return: True if the current player is under check
    """
    return board.position_in_check


def is_mate(board: Board, is_white: bool):
    """ Return if the current player is under mate.

    :param board: The board of the position
    :param is_white: Is the current player the white player
    :return: True if it is a mate for the opponent
    """
    pieces_dict = board.get_pieces_dict(is_white)
    king_cell = pieces_dict[PieceType.KING][0]
    if board.position_in_check:
        if not get_all_legal_moves(board, king_cell, PieceType.KING, is_white):
            if board.position_in_double_check:
                return True
            for piece in pieces_dict.keys():
                for cell in pieces_dict[piece]:
                    if get_all_legal_moves(board, cell, piece, is_white):
                        return False
            return True
    return False


def can_castle(board: Board, is_white: bool, move: Move):
    """ This method validates a castling move on a certain board

    :param board: The board on which we validate the move
    :param is_white: Whether the current player is white
    :param move: The move which is validated
    :return: True if the move is a legal castling move
    """

    if move.castle is False:
        return False
    if is_under_check(board):
        return False

    option = 'k' if move.is_king_side else 'q'
    direction = 1 if move.is_king_side else -1

    row = 1 if is_white else 8
    path = binary_ops_utils.translate_row_col_to_cell(row, 5 + direction)
    not_threatened = not (is_threatened(board, is_white, path)) and (1 << path) & board.get_board() == 0

    path = binary_ops_utils.translate_row_col_to_cell(row, 5 + 2 * direction)
    not_threatened = not (
        is_threatened(board, is_white,
                      binary_ops_utils.translate_row_col_to_cell(row, 5 + 2 * direction))) and not_threatened
    valid = (1 << path) & board.get_board() == 0 and not_threatened

    if not move.is_king_side:
        valid = valid and (1 << binary_ops_utils.translate_row_col_to_cell(row, 2)) & board.get_board() == 0

    if is_white:
        return valid and (option.upper() in board.castling_options)

    return option in board.castling_options and valid


def castle(board: Board, is_white: bool, move: Move, valid=False):
    """ This method perform a castling move on a board

    :param board: The board being used
    :param is_white: The color of the player
    :param move: The castling move
    :param valid: Flag that says if the move was validated beforehand
    """

    if move.castle is False:
        raise NonLegal()
    if (not valid) and is_under_check(board):
        raise KingUnderCheck()

    if not can_castle(board, is_white, move):
        raise NonLegal()

    row = 1 if is_white else 8
    col = 8 if move.is_king_side else 1
    side = -1 if move.is_king_side else 1
    king_cell = board.get_pieces_dict(is_white)[PieceType.KING][0]
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


def promote(board: Board, move: Move):
    """ Perform the promotion of the piece by switching the PieceType of the cell

    :param board: The board being used
    :param move: The promotion move
    """
    if move.promotion == PieceType.EMPTY:
        raise NonLegal()

    promotion_rank = 7 if board.is_white else 0
    if int(move.target / 8) != promotion_rank:
        raise NonLegal()

    board.remove_cell_piece(move.cell, PieceType.PAWN, board.is_white)
    board.set_cell_piece(move.cell, move.promotion, board.is_white)


def make_move(board: Board, move: Move, valid=True):
    """ Perform a move on the board and updates the required fields

    :param board: The board
    :param move: The move being performed
    :param valid: Flag that determine whether the move was validated
    """

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
        rook_row, rook_col = binary_ops_utils.translate_cell_to_row_col(move.cell)
        if board.is_white:
            if rook_row == 0:
                if rook_col == 0:
                    board.castling_options = ''.join([c for c in board.castling_options if c != 'Q'])
                elif rook_col == 7:
                    board.castling_options = ''.join([c for c in board.castling_options if c != 'K'])
        else:
            if rook_row == 0:
                if rook_col == 0:
                    board.castling_options = ''.join([c for c in board.castling_options if c != 'q'])
                elif rook_col == 7:
                    board.castling_options = ''.join([c for c in board.castling_options if c != 'k'])

    # Move the origin piece to the target and update the board
    board.remove_cell_piece(move.cell, piece, board.is_white)
    board.set_cell_piece(move.target, piece, board.is_white)
    board.update_round(move.target, piece, enable_en_passant)


def get_castle_moves(board: Board, is_white: bool):
    """ This method generate all possible castling moves for a player from certain position

    :param board: The position we use
    :param is_white: If the player is white
    :return: A list of possible castling moves
    """
    moves = []
    row = 1 if is_white else 8
    king_cell = board.get_pieces_dict(is_white)[PieceType.KING][0]
    move_1 = Move(king_cell, binary_ops_utils.translate_row_col_to_cell(row, 7))
    move_1.set_castle(True)
    if can_castle(board, is_white, move_1):
        moves.append(move_1)
    move_2 = Move(king_cell, binary_ops_utils.translate_row_col_to_cell(row, 3))
    move_2.set_castle(False)
    if can_castle(board, is_white, move_2):
        moves.append(move_2)
    return moves


def get_promotion_moves(move: Move):
    """ Returns a list of all legal promotion cases of a promotion move

    :param move: The promotion move
    :return: A list of all the possible promotions corresponding to the move
    """
    result = []
    relevant_pieces = [PieceType.QUEEN, PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP]
    for piece in relevant_pieces:
        tmp = Move(move.cell, move.target)
        tmp.set_promotion(piece)
        result.append(tmp)
    return result


def check_stalemate(board: Board):
    """ This method returns if the board is in stalemate case, note: I haven't considered all the stalemate rules

    :param board: The position we check
    :return: If the position is in stalemate
    """
    if board.count >= 50:
        return True

    return board.is_insufficient()


def fill_undo_info(board: Board, move: Move, enemy_type: PieceType) -> None:
    move.prev_castling = board.castling_options
    move.prev_en_passant = board.en_passant_ready
    move.enemy_type = enemy_type


