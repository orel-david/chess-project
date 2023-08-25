import Utils
import board
import pieces.piece
from chess_exceptions import KingSacrifice, KingNonLegal, KingUnderCheck, NonLegal
from graphics import GUI


def get_input():
    origin = input("Enter the cell of the piece you want to move: ")
    origin_move = Utils.translate_algebraic_notation_move(origin)
    if origin_move.castle:
        return origin_move
    destination = input("Enter the destination: ")
    return [origin_move, Utils.translate_algebraic_notation_move(destination)]


def print_winner(is_white):
    if not is_white:
        print("White won the game")
    else:
        print("Black won the game")


def print_stalemate():
    print("Stalemate, maybe the real win was the friends we made along the way")


def game():
    print("Welcome to chess game, when castling enter the algebraic notation in origin")
    print("When promoting enter in origin the pawn cell and in destination the letter of the piece")
    is_white = True
    gameboard = board.Board()
    gui = GUI()
    while not (Utils.is_mate(gameboard, is_white) or Utils.check_stalemate(gameboard)):
        gui.handle_events(gameboard)
        gameboard.print_board()
        gui.draw_board(gameboard)
        try:
            user_input = get_input()

            if type(user_input) is Utils.Move:
                Utils.castle(gameboard, is_white, user_input)
                is_white = not is_white
                continue

            origin_cell = gameboard.get_cell(user_input[0].row, user_input[0].col)
            if origin_cell is None:
                continue

            if origin_cell.is_white() != is_white:
                print("You must move your pieces")
                continue

            if origin_cell.get_cell_type() == pieces.piece.PieceType.EMPTY:
                print("You can't move empty cell")
                continue

            Utils.make_move(gameboard, origin_cell, user_input[1])
            is_white = not is_white
        except NonLegal:
            print("Illegal move, try again")
        except KingSacrifice:
            print("You can't move a locked piece, try again")
        except KingUnderCheck:
            print("You need to move your king out of danger, try again")
        except KingNonLegal:
            print("You can't sacrifice your king, try again")

    gameboard.print_board()
    if Utils.is_mate(gameboard, is_white):
        print_winner(is_white)
    else:
        print_stalemate()


game()
