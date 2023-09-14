import binary_ops_utils
from board import Board
from piece import PieceType


class Move:
    # cell and target are cell index
    cell: int
    target: int
    castle: bool
    is_king_side: bool
    is_en_passant: bool
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
            moves.append(move)

    if board.is_type_of(cell, PieceType.KING):
        moves += get_castle_moves(board, board.is_cell_colored(cell, True))

    return moves


def condition(board: Board, move: Move, piece: PieceType, is_white: bool):
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
# def castle(board: Board, is_white: bool, move: Move):
#     if move.castle is False:
#         raise NonLegal()
#     if is_under_check(board, is_white):
#         raise KingUnderCheck()
#
#     row = 1 if is_white else 8
#     col = 8 if move.is_king_side else 1
#     king_cell = board.get_pieces_dict(is_white)[PieceType.KING][0]
#     king = king_cell.get_cell_piece()
#     rook_cell = board.get_cell(row, col)
#     rook = rook_cell.get_cell_piece()
#     if king.moved or rook_cell.get_cell_type() != PieceType.ROOK or rook.moved:
#         raise NonLegal()
#
#     direction = 1 if move.is_king_side else -1
#     moves = [Move(row, 5 + direction), Move(row, 5 + 2 * direction)]
#     cond = (lambda m: board.get_cell(m.row, m.col).is_empty() and (
#         not is_threatened(board, is_white, board.get_cell(m.row, m.col))))
#     legal = all(cond(m) for m in moves)
#     if legal:
#         king_cell.cell_piece = Piece(False)
#         rook_cell.cell_piece = Piece(False)
#         king.moved = True
#         rook.moved = True
#         board.get_cell(row, moves[1].col).cell_piece = king
#         board.get_cell(row, moves[0].col).cell_piece = rook
#         pieces_dict = board.get_pieces_dict(is_white)
#         pieces_dict[PieceType.KING] = [board.get_cell(row, moves[1].col)]
#         pieces_dict[PieceType.ROOK] = [board.get_cell(row, moves[0].col) if c == rook_cell else c for c in
#                                        pieces_dict[PieceType.ROOK]]
#
#
# def update_en_passant(board: Board, cell: Cell, move: Move):
#     if move.is_en_passant:
#         pawn_advancement = 1 if cell.is_white() else -1
#         enemy = board.get_cell(move.row - pawn_advancement, move.col)
#         enemy.cell_piece = Piece(False)
#         enemy_dict = board.get_pieces_dict(not cell.is_white())
#         enemy_dict[PieceType.PAWN] = [c for c in enemy_dict[PieceType.PAWN] if c != enemy]
#     if board.en_passant_ready is not None:
#         board.en_passant_ready.en_passant = False
#         board.en_passant_ready = None
#
#
# def update_piece(board: Board, cell: Cell, move: Move, origin_cell: Cell):
#     if cell.get_cell_type() == PieceType.KING or cell.get_cell_type() == PieceType.ROOK:
#         cell.get_cell_piece().moved = True
#
#     if cell.get_cell_type() == PieceType.PAWN:
#         board.count = 0
#         pawn = cell.get_cell_piece()
#         pawn.start = False
#         pawn.en_passant = True if abs(origin_cell.get_row() - move.row) == 2 else False
#         if pawn.en_passant:
#             board.en_passant_ready = pawn
#     board.count = board.count + 1
#
#
# def promote(board: Board, cell: Cell, move: Move):
#     if move.promotion == PieceType.EMPTY:
#         raise NonLegal()
#     if cell.get_cell_type() != PieceType.PAWN:
#         raise NonLegal()
#     promotion_rank = 8 if cell.is_white() else 1
#     if move.row != promotion_rank:
#         raise NonLegal()
#
#     pieces_dict = board.get_pieces_dict(cell.is_white())
#     color = cell.is_white()
#     if move.promotion == PieceType.ROOK:
#         piece = pieces.rook.Rook(color)
#     elif move.promotion == PieceType.BISHOP:
#         piece = pieces.bishop.Bishop(color)
#     elif move.promotion == PieceType.KNIGHT:
#         piece = pieces.knight.Knight(color)
#     else:
#         piece = pieces.queen.Queen(color)
#     cell.cell_piece = piece
#     pieces_dict[move.promotion].append(cell)
#     pieces_dict[PieceType.PAWN] = [c for c in pieces_dict[PieceType.PAWN] if c != cell]
#
#
# def check_stops_check(board: Board, cell: Cell, move: Move):
#     piece_dict = board.get_pieces_dict(cell.is_white())
#     enemy_dict = board.get_pieces_dict(not cell.is_white())
#     king_cell = piece_dict[PieceType.KING][0]
#     curr_cell = board.get_cell(move.row, move.col)
#     prev_piece = curr_cell.get_cell_piece()
#     curr_cell.cell_piece = cell.cell_piece
#     cell.cell_piece = Piece(False)
#     if not curr_cell.is_empty():
#         piece_dict[curr_cell.get_cell_type()] = [c if c != cell else curr_cell for
#                                                  c in piece_dict[curr_cell.get_cell_type()]]
#     if prev_piece.piece_type != PieceType.EMPTY:
#         enemy_dict[prev_piece.piece_type] = [c for c in enemy_dict[prev_piece.piece_type] if
#                                              c != curr_cell]
#     result = is_under_check(board, curr_cell.is_white())
#     if prev_piece.piece_type != PieceType.EMPTY:
#         enemy_dict[prev_piece.piece_type].append(curr_cell)
#     if not curr_cell.is_empty():
#         piece_dict[curr_cell.get_cell_type()] = [c if c != curr_cell else cell for
#                                                  c in piece_dict[curr_cell.get_cell_type()]]
#     piece_dict[PieceType.KING] = [king_cell]
#     cell.cell_piece = curr_cell.cell_piece
#     curr_cell.cell_piece = prev_piece
#     return not result
#
#
# def make_move(board: Board, cell: Cell, move: Move, valid=False):
#     if move.castle:
#         castle(board, cell.is_white(), move)
#
#     if move.promotion != PieceType.EMPTY:
#         promote(board, cell, move)
#
#     target_cell = board.get_cell(move.row, move.col)
#     if target_cell.get_cell_type() != PieceType.EMPTY:
#         board.count = 0
#         pieces_dict = board.get_pieces_dict(target_cell.is_white())
#         pieces_dict[target_cell.get_cell_type()] = [c for c in pieces_dict[target_cell.get_cell_type()] if
#                                                     c != target_cell]
#     pieces_dict = board.get_pieces_dict(cell.is_white())
#     pieces_dict[cell.get_cell_type()] = [target_cell if c == cell else c for c in pieces_dict[cell.get_cell_type()]]
#     target_cell.cell_piece = cell.get_cell_piece()
#     cell.cell_piece = Piece(False)
#     update_en_passant(board, target_cell, move)
#     update_piece(board, target_cell, move, cell)


def get_castle_moves(board: Board, is_white: bool):
    moves = []
    row = 1 if is_white else 8
    move_1 = Move(row, 7)
    move_1.set_castle(True)
    if can_castle(board, is_white, move_1):
        moves.append(move_1)
    move_2 = Move(row, 3)
    move_2.set_castle(False)
    if can_castle(board, is_white, move_2):
        moves.append(move_2)
    return moves


def check_stalemate(board: Board):
    if board.count >= 50:
        return True

    return board.is_insufficient()
