import time
import core
from core import Board
from core import Transposition_table
import evaluation_utils

search_table = Transposition_table(0x8000000)

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
    global search_table
    entry = search_table.get_entry(board.zobrist_key)
    
    if entry is not None and entry.zobrist_key == board.zobrist_key and entry.depth >= depth:
        score = entry.score if entry.is_white == board.is_white else -entry.score
        if entry.node_type == 0:
            return score
        if entry.node_type == 1 and score >= beta:
            alpha = max(score, alpha)
        elif entry.node_type == 2 and score <= alpha:
            beta = min(beta, score)
            
        if alpha >= beta:
            return beta
            
    if depth <= 0:
        return quiescence_search(board, 4, alpha, beta)
    
    piece_dict = board.get_pieces_dict(board.is_white)
    moves = []
    for piece in board.pieces_dict.values():
        for cell in piece_dict[piece]:
            moves += core.core_utils.get_all_legal_moves(board, cell, piece, board.is_white)

    if not moves:
        if board.position_in_check:
            return float('-inf')
        return 0

    moves = list(filter(lambda move: evaluation_utils.move_prediction(board, move), moves))

    best_move = None
    best_val = float("-inf")
    score = 0
    bound = 2
    for move in moves:
        core.core_utils.make_move(board, move, True)
        extra = 1 if board.position_in_check else 0
        score = -search_position(board, depth - 1 + extra, -beta, -alpha)
        core.core_utils.undo_move(board, move)

        if best_val <= score:
            best_val = score
            best_move = move

        if score >= beta:
            search_table.store_entry(board.zobrist_key, beta, depth, 1, move, board.is_white)
            return beta

        if score > alpha:
            bound = 0
            alpha = score
            best_move = move

    search_table.store_entry(board.zobrist_key, best_val, depth, bound, best_move, board.is_white)


    return alpha


def search_move(board: Board, depth: int) -> core.Move:
    """ This method returns the best move by searching to a certain depth

    :param board: The position in which we search
    :param depth: The depth of the search
    :return: The move which according to the evaluate metric is the best.
    """
    best_val = float("-inf")
    global search_table
    entry = search_table.get_entry(board.zobrist_key)
    
    if entry is not None and entry.zobrist_key == board.zobrist_key and entry.depth >= depth:
        if entry.is_white == board.is_white:
            if entry.node_type == 0:
                return entry.best
            elif entry.node_type == 1:
                best_val = entry.score
        
    piece_dict = board.get_pieces_dict(board.is_white)
    moves = []

    for piece in board.pieces_dict.values():
        for cell in piece_dict[piece]:
            moves += core.core_utils.get_all_legal_moves(board, cell, piece, board.is_white)

    if not moves:
        return None

    best_move = None
    moves = list(filter(lambda move: evaluation_utils.move_prediction(board, move), moves))
    for move in moves:
        core.core_utils.make_move(board, move, True)
        val = -search_position(board, depth - 1, best_val, float("inf"))
        core.core_utils.undo_move(board, move)

        if val >= best_val:
            best_move = move
            best_val = val
            
    search_table.store_entry(board.zobrist_key, best_val, depth, 0, best_move, board.is_white)

    return best_move
