from core.core_utils import Move
from core import Board
from core import PieceType
from core import translate_cell_to_row_col
from core import core_utils

pieces_dict = {PieceType.QUEEN: 'q', PieceType.ROOK: 'r', PieceType.BISHOP: 'b', PieceType.KNIGHT: 'n',
               PieceType.KING: 'k', PieceType.PAWN: 'p'}
notation_dict = {'Q': PieceType.QUEEN, 'R': PieceType.ROOK, 'B': PieceType.BISHOP, 'N': PieceType.KNIGHT,
                 'K': PieceType.KING}


def convert_move_to_uci(move: Move) -> str:
    """ This method converts a move to string representation according to UCI protocol

    :param move: The move we convert
    :return: The string which represent the move.
    """
    suffix = pieces_dict[move.promotion] if move.promotion != PieceType.EMPTY else ''
    return convert_cell_to_algebraic_notation(move.cell) + convert_cell_to_algebraic_notation(move.target) + suffix


def convert_algebraic_to_move(notation: str, board: Board) -> Move:
    """ This function decode algebraic notation of move to a Move instance if possible

    :param notation: The string of which represent the algebraic notation
    :param board: The board of the game
    :return: Corresponding move
    """
    if notation == 'o-o':
        move = Move(0, 0)
        move.set_castle(True)
        return move

    if notation == 'o-o-o':
        move = Move(0, 0)
        move.set_castle(False)
        return move

    is_white = board.is_white
    pieces = board.get_pieces_dict(is_white)
    piece_type = notation_dict[notation[0]] if notation[0].isupper() else PieceType.PAWN
    cells = pieces[piece_type]
    origin_file = -1
    origin_rank = -1
    target_file = -1
    target_rank = -1
    promotion = PieceType.EMPTY
    start = 0 if piece_type == PieceType.PAWN else 1

    for c in notation[start:]:
        if c == 'x' or c == '=' or c == '+':
            pass
        elif c.isalpha():
            if c.isupper():
                promotion = notation_dict[c]
            elif target_file == -1:
                target_file = ord(c) - ord('a')
            else:
                origin_file = target_file
                target_file = ord(c) - ord('a')
        elif c.isdigit():
            if target_rank == -1:
                target_rank = int(c) - 1
            else:
                origin_rank = target_rank
                target_rank = int(c) - 1
        else:
            # Illegal move notation
            return None

    if target_rank == -1 or target_file == -1:
        return None

    target = target_rank * 8 + target_file
    for cell in cells:
        rank, file = translate_cell_to_row_col(cell)

        if ((origin_rank != -1) and (rank != origin_rank)) or ((origin_file != -1) and (file != origin_file)):
            continue

        move = Move(cell, target)
        if promotion != PieceType.EMPTY:
            move.set_promotion(promotion)

        if core_utils.is_pseudo_legal(board, move) and core_utils.condition(board, move, piece_type, is_white):
            return move
    return None


def convert_cell_to_algebraic_notation(cell: int) -> str:
    """ This method convert cell index to the algebraic notation of the corresponding cell

    :param cell: The index of the cell
    :return: The algebraic notation of the cell
    """
    row, col = (int(cell / 8), cell % 8)
    return (chr(col + ord('a'))) + str(row + 1)


def convert_move_algebraic(board: Board, move: Move) -> str:
    if move.castle:
        if move.is_king_side:
            return "o-o"
        return "o-o-o"

    piece_type = board.get_cell_type(move.cell)
    pieces = board.get_pieces_dict(board.is_white)
    notation = '' if piece_type == PieceType.PAWN else pieces_dict[piece_type].upper()
    rank, file = translate_cell_to_row_col(move.cell)
    specify_file = False
    specify_rank = False

    for cell in pieces[piece_type]:
        if cell == move.cell or piece_type == PieceType.PAWN:
            continue

        tmp_rank, tmp_file = translate_cell_to_row_col(cell)

        tmp_move = Move(cell, move.target)
        if move.promotion != PieceType.EMPTY:
            tmp_move.set_promotion(move.promotion)

        is_legal = core_utils.is_pseudo_legal(board, tmp_move) and core_utils.condition(board, tmp_move, piece_type,
                                                                                        board.is_white)
        if is_legal:
            if tmp_file != file:
                specify_file = True
            elif tmp_rank != rank:
                specify_rank = True

    is_capture = not board.is_cell_empty(move.target)
    if specify_file or (piece_type == PieceType.PAWN and is_capture):
        notation = notation + (chr(file + ord('a')))
    if specify_rank:
        notation = notation + str(rank + 1)

    if is_capture:
        notation = notation + 'x'

    notation = notation + convert_cell_to_algebraic_notation(move.target)
    return notation if move.promotion == PieceType.EMPTY else notation + "=" + pieces_dict[move.promotion].upper()