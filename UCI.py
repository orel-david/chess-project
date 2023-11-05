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


def convert_uci_to_move(notation: str, board: Board) -> Move:
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

    for c in notation[1:]:
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
