import binary_ops_utils
from Utils import Move
from piece import PieceType

pieces_dict = {PieceType.QUEEN: 'q', PieceType.ROOK: 'r', PieceType.BISHOP: 'b', PieceType.KNIGHT: 'n',
               PieceType.KING: 'k', PieceType.PAWN: 'p'}


def convert_move_to_uci(move: Move) -> str:
    """ This method converts a move to string representation according to UCI protocol

    :param move: The move we convert
    :return: The string which represent the move.
    """
    suffix = pieces_dict[move.promotion] if move.promotion != PieceType.EMPTY else ''
    return convert_cell_to_algebraic_notation(move.cell) + convert_cell_to_algebraic_notation(move.target) + suffix


def convert_cell_to_algebraic_notation(cell: int) -> str:
    """ This method convert cell index to the algebraic notation of the corresponding cell

    :param cell: The index of the cell
    :return: The algebraic notation of the cell
    """
    row, col = binary_ops_utils.translate_cell_to_row_col(cell)
    return (chr(col + ord('a'))) + str(row + 1)
