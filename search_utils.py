import core
from core import Board


def count_nodes(gboard: Board, depth: int) -> int:
    """ The method counts all the nodes from a certain position up to a certain depth

    :param gboard: The initial position
    :param depth: The depth of the search
    :return: The amount of possible position in specified depth from gboard position.
    """
    if depth <= 0:
        return 1
    sum_options = 0

    piece_dict = gboard.get_pieces_dict(gboard.is_white)
    moves = []
    for piece in gboard.pieces_dict.values():
        for cell in piece_dict[piece]:
            moves += core.core_utils.get_all_legal_moves(gboard, cell, piece, gboard.is_white)

    for move in moves:
        core.core_utils.make_move(gboard, move, True)
        sum_options += count_nodes(gboard, depth - 1)
        core.core_utils.undo_move(gboard, move)
    return sum_options
