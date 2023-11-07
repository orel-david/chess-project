import search_utils
from opening import opener
from core import Board, Move
from UCI import convert_move_algebraic


class Bot:
    """
    This class represent the chess bot
    """

    def __init__(self):
        self.opener = opener.Opener()
        self.opening = True

    def think(self, board: Board) -> Move:
        """ This method is used to get the move the bot thinks is best in the position

        :param board: The board instance that represents the position
        :return: The move which the bot thinks is the best
        """
        if self.opening:
            move = self.opener.get_move()
            if move is not None:
                self.opener.add_to_line(convert_move_algebraic(board, move))
                return move

        return search_utils.search_move(board)

    def update_line(self, board: Board, move: Move) -> None:
        """ This method updates the move which was made by the opponent, for now only for the opener

        :param board: The position
        :param move: The move which was made
        """
        if not self.opening:
            return

        self.opener.add_to_line(convert_move_algebraic(board, move))
