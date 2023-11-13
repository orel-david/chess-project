import core
from core import Board
from graphics import GUI


def determine_result(gboard: Board, is_white: bool):
    """ This method receives a board of an ended game and returns the board's result.

    :param gboard: The gameboard
    :param is_white: The color of the current player
    :return: 0 if draw, 1 if white won, -1 if black won
    """
    if core.core_utils.check_stalemate(gboard):
        return 0
    else:
        return -1 if is_white else 1


def game():
    """
    This is the game main function which initialize the board and GUI and starts the game loop
    """
    gameboard = Board()
    gui = GUI(gameboard.is_white)
    while not (core.core_utils.is_mate(gameboard, gui.is_white()) or core.core_utils.check_stalemate(gameboard)):
        gui.handle_events(gameboard)

    gui.end(determine_result(gameboard, gui.is_white()))


if __name__ == "__main__":
    game()
