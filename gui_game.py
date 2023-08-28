import Utils
import board
from graphics import GUI


def determine_result(gboard: board.Board, is_white: bool):
    if Utils.check_stalemate(gboard):
        return 0
    else:
        return -1 if is_white else 1


def game():
    gameboard = board.Board()
    gui = GUI()
    gui.draw_board(gameboard)
    while not (Utils.is_mate(gameboard, gui.is_white()) or Utils.check_stalemate(gameboard)):
        gui.handle_events(gameboard)

    gui.end(determine_result(gameboard, gui.is_white()))


game()
