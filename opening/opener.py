import os
import random


class Opener:
    """
    This class provides an interface to an opening book
    """
    game_database = "formatted_games.txt"
    database_path = os.path.join("opening", game_database)

    def __init__(self):
        self.ply = 0
        with open(self.database_path, 'r') as in_file:
            self.games = in_file.readlines()
        self.amount = len(self.games)
        self.line = ''

    def add_to_line(self, move: str) -> None:
        """ This method adds another move as restriction for the search

        :param move: The algebraic notation of the move made
        """
        self.ply += 1
        self.line = self.line + " " + move if self.line != "" else move
        self.games = [game for game in self.games if (game.startswith(self.line) and (len(game.split(" ")) > self.ply))]
        self.amount = len(self.games)

    def get_move(self) -> str:
        """
        :return: This method returns a random move algebraic notation for a possible move.
        """
        if self.amount == 0:
            return ""

        game_index = random.randint(0, self.amount - 1)
        game = self.games[game_index]
        game = game.split(" ")
        return game[self.ply]
