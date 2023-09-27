import binary_ops_utils
from Utils import Move
from piece import PieceType

pieces_dict = {'q': PieceType.QUEEN, 'r': PieceType.ROOK, 'b': PieceType.BISHOP, 'n': PieceType.KNIGHT,
               'k': PieceType.KING, 'p': PieceType.PAWN}


def convert_move_to_uci(move: Move):
    suffix = pieces_dict[move.promotion] if move.promotion != PieceType.EMPTY else ''
    return convert_cell_to_algebraic_notation(move.cell) + convert_cell_to_algebraic_notation(move.target) + suffix


def convert_cell_to_algebraic_notation(cell: int):
    row, col = binary_ops_utils.translate_cell_to_row_col(cell)
    return (chr(col + ord('a'))) + str(row + 1)

