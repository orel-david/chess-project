import core
from core import Board
from graphics import GUI


def determine_result(gboard: Board, is_white: bool, is_stalemate: bool):
    """ This method receives a board of an ended game and returns the board's result.

    :param gboard: The gameboard
    :param is_white: The color of the current player
    :return: 0 if draw, 1 if white won, -1 if black won
    """
    if is_stalemate:
        return 0
    else:
        return -1 if is_white else 1


def game():
    """
    This is the game main function which initialize the board and GUI and starts the game loop
    """
    gameboard = Board()
    gui = GUI(gameboard.is_white)
    is_stalemate = gui.is_repetition(gameboard) or core.core_utils.check_stalemate(gameboard)
    while not (core.core_utils.is_mate(gameboard, gui.is_white()) or is_stalemate):
        gui.handle_events(gameboard)
        is_stalemate = gui.is_repetition(gameboard) or core.core_utils.check_stalemate(gameboard)


    gui.end(determine_result(gameboard, gui.is_white(), is_stalemate))


if __name__ == "__main__":
    game()
