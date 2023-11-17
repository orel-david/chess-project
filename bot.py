import time

import search_utils
from opening import Opener
from core import Board, Move
from UCI import convert_move_algebraic, convert_algebraic_to_move


class Bot:
    """
    This class represent the chess bot
    """

    def __init__(self):
        self.opener = Opener()
        self.opening = True

    def think(self, board: Board) -> Move:
        """ This method is used to get the move the bot thinks is best in the position

        :param board: The board instance that represents the position
        :return: The move which the bot thinks is the best
        """
        start = time.time()
        if self.opening:
            move_notation = self.opener.get_move()
            if move_notation != "":
                move = convert_algebraic_to_move(move_notation, board) 
            else:
                move = None
                
            if move is not None:
                print(move_notation)
                self.opener.add_to_line(move_notation)
                print(time.time() - start)

                return move
        move = search_utils.search_move(board)
        print(time.time() - start)
        return move

    def update_line(self, board: Board, move: Move) -> None:
        """ This method updates the move which was made by the opponent, for now only for the opener

        :param board: The position
        :param move: The move which was made
        """
        if not self.opening:
            return

        self.opener.add_to_line(convert_move_algebraic(board, move))
