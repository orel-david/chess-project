import binary_ops_utils
from board import Board
from chess_exceptions import NonLegal, KingUnderCheck
from piece import PieceType


class Move:
    # cell and target are cell index
    cell: int
    target: int
    castle: bool
    is_king_side: bool
    promotion: PieceType

    def __init__(self, cell, tar):
        self.cell = cell
        self.target = tar
        self.castle = False
        self.is_king_side = False
        self.is_en_passant = False
        self.promotion = PieceType.EMPTY

    def set_castle(self, is_right):
        self.castle = True
        self.is_king_side = is_right

    def set_promotion(self, piece):
        self.promotion = piece


def is_pseudo_legal(board: Board, move: Move):
    moves = board.get_moves_by_cell(move.cell, board.is_white)
    return moves & binary_ops_utils.switch_cell_bit(0, move.target, True) != 0


def is_threatened(board: Board, is_white: bool, cell: int):
    return binary_ops_utils.switch_cell_bit(0, cell, True) & board.get_attacks(is_white) != 0


def get_all_legal_moves(board: Board, cell: int, piece: PieceType, is_white: bool):
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

    if board.is_type_of(cell, PieceType.KING):
        moves += get_castle_moves(board, board.is_cell_colored(cell, True))

    return moves


def condition(board: Board, move: Move, piece: PieceType, is_white: bool):
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
        if (1 << move.target) & board.check_map != 0:
            return True

        if board.pin_map != 0:
            if abs(board.pin_map) == abs(step):
                for cell_tmp in range(cell, king_cell, step):
                    if not board.is_cell_empty(cell_tmp):
                        return False
                return True
        return False

    if not board.is_pinned(cell, is_white)[0]:
        return True

    return abs(binary_ops_utils.get_direction(move.cell, king_cell)) == abs(step)


def get_threats(board: Board, is_white: bool, cell: int):
    threats = []
    enemy_pieces = board.get_pieces_dict(not is_white)
    for piece in enemy_pieces:
        for enemy in enemy_pieces[piece]:
            if is_pseudo_legal(board, Move(enemy, cell)) and board.is_cell_colored(cell, True):
                threats.append(enemy)
    return threats


def is_under_check(board: Board):
    return board.position_in_check


def is_mate(board: Board, is_white: bool):
    pieces_dict = board.get_pieces_dict(is_white)
    king_cell = pieces_dict[PieceType.KING][0]
    if board.position_in_check:
        if (~board.get_attacks(is_white)) & board.get_king_cell_moves(king_cell, is_white) == 0:
            if board.position_in_double_check:
                return True
            for piece in pieces_dict.keys():
                for cell in pieces_dict[piece]:
                    if get_all_legal_moves(board, cell, piece, is_white):
                        return False
            return True
    return False


def can_castle(board: Board, is_white: bool, move: Move):
    if move.castle is False:
        return False
    if is_under_check(board):
        return False

    option = 'k' if move.is_king_side else 'q'
    direction = 1 if move.is_king_side else -1

    row = 1 if is_white else 8
    path = 0
    path = binary_ops_utils.switch_bit(path, row, 5 + direction, True)
    not_threatened = not (is_threatened(board, is_white, path))

    path = binary_ops_utils.switch_bit(path, row, 5 + 2 * direction, True)
    not_threatened = not (
        is_threatened(board, is_white,
                      binary_ops_utils.translate_row_col_to_cell(row, 5 + 2 * direction))) and not_threatened
    valid = path & board.get_board() == 0 and not_threatened
    if is_white and option in board.castling_options:
        return valid

    return (option.upper() in board.castling_options) and valid


# TODO:CONTINUE FROM HERE
def castle(board: Board, is_white: bool, move: Move, valid=False):
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


def promote(board: Board, move: Move):
    if move.promotion == PieceType.EMPTY:
        raise NonLegal()

    promotion_rank = 7 if board.is_white else 0
    if int(move.target / 8) != promotion_rank:
        raise NonLegal()

    board.remove_cell_piece(move.cell, PieceType.PAWN, board.is_white)
    board.remove_cell_piece(move.cell, move.promotion, board.is_white)


def make_move(board: Board, move: Move, valid=True):
    piece = board.get_cell_type(move.cell)
    enable_en_passant = False
    if move.castle:
        castle(board, board.is_white, move)
        return

    if move.promotion != PieceType.EMPTY and piece == PieceType.PAWN:
        promote(board, move)

    if not valid:
        if not condition(board, move, piece, board.is_white):
            raise NonLegal()

    target_type = board.get_cell_type(move.target)
    if target_type != PieceType.EMPTY:
        board.count = 0
        board.remove_cell_piece(move.target, target_type, not board.is_white)

    if piece == PieceType.PAWN:
        board.count = 0
        diff = abs(move.cell - move.target)
        # If move 2 rows it can be subject to en passant
        if diff == 16:
            enable_en_passant = True

        # Check if en Passant
        if target_type == PieceType.EMPTY and (abs(move.cell - move.target) % 8 != 0):
            side = 1 if (move.cell % 8) < (move.target % 8) else -1
            board.remove_cell_piece(move.cell + side, PieceType.PAWN, not board.is_white)
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
    board.remove_cell_piece(move.cell, piece, board.is_white)
    board.set_cell_piece(move.cell, piece, board.is_white)
    board.update_round(move.target, piece, enable_en_passant)


def get_castle_moves(board: Board, is_white: bool):
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
    result = []
    relevant_pieces = [PieceType.QUEEN, PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP]
    for piece in relevant_pieces:
        tmp = Move(move.cell, move.target)
        tmp.set_promotion(piece)
        result.append(tmp)
    return result


def check_stalemate(board: Board):
    if board.count >= 50:
        return True

    return board.is_insufficient()
