import time
import core
from core import Board
import evaluation_utils


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


def quiescence_search(board: Board, depth_limit: int, alpha: int, beta:int) -> float:
    eval = evaluation_utils.evaluate(board)
    
    if depth_limit == 0:
        return eval
    if eval >= beta:
        return beta
    if eval > alpha:
        alpha = eval
        
    piece_dict = board.get_pieces_dict(board.is_white)
    moves = []
    for piece in board.pieces_dict.values():
        for cell in piece_dict[piece]:
            moves += core.core_utils.get_all_legal_captures(board, cell, piece, board.is_white)
            
    for move in moves:
        core.core_utils.make_move(board, move, True)
        eval = -quiescence_search(board, depth_limit - 1, -beta, -alpha)
        core.core_utils.undo_move(board, move)
        if eval >= beta:
            return beta
        if eval > alpha:
            alpha = eval
    
    return alpha


def search_position(board: Board, depth: int, alpha: int, beta: int) -> float:
    """ This method uses alpha beta pruning to estimate how well is the position looking to a certain depth.

    :param board: The position
    :param depth: The depth to which we look
    :param alpha: The alpha value
    :param beta: The beta value
    :return: The estimate of the position
    """
    if depth <= 0:
        return quiescence_search(board, 2, alpha, beta)
    
    piece_dict = board.get_pieces_dict(board.is_white)
    moves = []
    for piece in board.pieces_dict.values():
        for cell in piece_dict[piece]:
            moves += core.core_utils.get_all_legal_moves(board, cell, piece, board.is_white)

    if not moves:
        if board.position_in_check:
            return float('-inf')
        return 0

    score = 0
    for move in moves:
        core.core_utils.make_move(board, move, True)
        extra = 1 if board.position_in_check else 0
        score = -search_position(board, depth - 1 + extra, -beta, -alpha)
        core.core_utils.undo_move(board, move)

        if score >= beta:
            return beta

        alpha = max(alpha, score)

    return alpha


def search_move(board: Board, depth: int) -> core.Move:
    """ This method returns the best move by searching to a certain depth

    :param board: The position in which we search
    :param depth: The depth of the search
    :return: The move which according to the evaluate metric is the best.
    """
    evaluation_utils.init_tables()
    piece_dict = board.get_pieces_dict(board.is_white)
    moves = []

    for piece in board.pieces_dict.values():
        for cell in piece_dict[piece]:
            moves += core.core_utils.get_all_legal_moves(board, cell, piece, board.is_white)

    if not moves:
        return None

    best_move = None

    for move in moves:
        core.core_utils.make_move(board, move, True)
        val = -search_position(board, depth - 1, best_val, float("inf"))
        core.core_utils.undo_move(board, move)

        if val >= best_val:
            best_move = move
            best_val = val

    return best_move
