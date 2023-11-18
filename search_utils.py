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


def quiescence_search(board: Board, depth_limit: int, alpha: float, beta: float) -> float:
    position_eval = evaluation_utils.evaluate(board)

    if depth_limit == 0:
        return position_eval
    if position_eval >= beta:
        return beta
    if position_eval > alpha:
        alpha = position_eval

    piece_dict = board.get_pieces_dict(board.is_white)
    moves = []
    for piece in board.pieces_dict.values():
        for cell in piece_dict[piece]:
            moves += core.core_utils.get_all_legal_captures(board, cell, piece, board.is_white)

    for move in moves:
        core.core_utils.make_move(board, move, True)
        position_eval = -quiescence_search(board, depth_limit - 1, -beta, -alpha)
        core.core_utils.undo_move(board, move)
        if position_eval >= beta:
            return beta
        if position_eval > alpha:
            alpha = position_eval

    return alpha


def search_position(board: Board, depth: int, alpha: float, beta: float, root_distance=0) -> float:
    """ This method uses alpha beta pruning to estimate how well is the position looking to a certain depth.

    :param board: The position
    :param depth: The depth to which we look
    :param alpha: The alpha value
    :param beta: The beta value
    :return: The estimate of the position
    """
    global search_table
    entry = search_table.get_entry(board.zobrist_key)
    valid = (entry is not None) and (entry.is_white == board.is_white)
    alpha_origin = alpha
    
    if valid and entry.zobrist_key == board.zobrist_key and entry.depth >= depth:
        score = entry.score
        if entry.node_type == 0:
            return score
        if entry.node_type == 1:
            alpha = max(score, alpha)
        elif entry.node_type == 2:
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
            return float('-inf') + root_distance
        return 0

    moves.sort(key=lambda m: evaluation_utils.move_prediction(board, m), reverse=True)

    best_move = None
    for move in moves:
        core.core_utils.make_move(board, move, True)
        extra = 1 if board.position_in_check else 0
        score = -search_position(board, depth - 1 + extra, -beta, -alpha, root_distance + 1)
        core.core_utils.undo_move(board, move)

        if score >= beta:
            search_table.store_entry(board.zobrist_key, beta, depth, 1, move, board.is_white)
            return beta

        if score > alpha:
            alpha = score
            best_move = move

    bound = 2 if alpha_origin >= alpha else 0
    search_table.store_entry(board.zobrist_key, alpha, depth, bound, best_move, board.is_white)

    return alpha


def search_move(board: Board, time_limit=4, min_depth = 3) -> core.Move:
    """ This method returns the best move by searching to a certain depth

    :param board: The position in which we search
    :param time_limit: The time allocated for the search in the position
    :return: The move which according to the evaluate metric is the best.
    """
    moves_values = {}
    start_time = time.time()
    best_val = float("-inf")
    global search_table

    piece_dict = board.get_pieces_dict(board.is_white)
    moves = []

    for piece in board.pieces_dict.values():
        for cell in piece_dict[piece]:
            moves += core.core_utils.get_all_legal_moves(board, cell, piece, board.is_white)

    if not moves:
        return None

    best_move = None
    moves.sort(key=lambda m: evaluation_utils.move_prediction(board, m), reverse=True)
    depth = min_depth
    
    while (time.time() - start_time) < time_limit:
        for move in moves:
            core.core_utils.make_move(board, move, True)
            val = -search_position(board, depth - 1, float("-inf"), -best_val)
            core.core_utils.undo_move(board, move)

            moves_values[move] = val
            if val > best_val:
                best_move = move
                best_val = val
                
            if best_val == float("inf"):
                return best_move
            
            if time.time() - start_time >= time_limit:
                search_table.store_entry(board.zobrist_key, best_val, depth, 1, move, board.is_white)
                return best_move
            
        moves.sort(key=lambda m: moves_values[m], reverse=True)
        depth += 1

    search_table.store_entry(board.zobrist_key, best_val, depth, 0, best_move, board.is_white)
    return best_move
