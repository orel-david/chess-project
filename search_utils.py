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

def search_position(board: Board, depth: int, alpha: int, beta:int) -> float:
    if depth <= 0:
        return evaluation_utils.evaluate(board)
    
    piece_dict = board.get_pieces_dict(board.is_white)
    moves = []
    for piece in board.pieces_dict.values():
        for cell in piece_dict[piece]:
            moves += core.core_utils.get_all_legal_moves(board, cell, piece, board.is_white)
    
    if moves == []:
        if board.position_in_check:
            return float('-inf')
        return 0
    
    score = 0
    for move in moves:
        core.core_utils.make_move(board, move, True)
        score = -search_position(board, depth - 1, -beta, -alpha)
        core.core_utils.undo_move(board, move)
        
        if score >= beta:
            return beta
        
        alpha = max(alpha, score)    
        
    return alpha
        
def search_move(board : Board, depth: int) -> core.Move:
    evaluation_utils.init_tables()
    piece_dict = board.get_pieces_dict(board.is_white)
    moves = []
    
    for piece in board.pieces_dict.values():
        for cell in piece_dict[piece]:
            moves += core.core_utils.get_all_legal_moves(board, cell, piece, board.is_white)
            
    if moves == []:
        return None
    
    bestMove = None
    bestVal = float("-inf")
    
    for move in moves:
        core.core_utils.make_move(board, move, True)
        val = -search_position(board, depth - 1, float("-inf"), float("inf"))
        core.core_utils.undo_move(board, move)

        if val >= bestVal:
            bestMove = move
            bestVal = val
    
    return bestMove
    
    