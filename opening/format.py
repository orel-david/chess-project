import os
import re

pattern = r'\d+\.'
input_file = "lichess_games.pgn"
output_file = "formatted_games.txt"

input_path = os.path.join("opening", input_file)
output_path = os.path.join("opening", output_file)

with open(input_path, 'r') as ifile, open(output_path, 'w') as ofile:
    game = []
    for line in ifile:
        if line.strip() and line[0] != '[':
            moves = re.sub(pattern, '', line).split(" ")
            moves = [c.replace("\n", "") for c in moves if c != '' and c != '\n']
            moves = [c.replace("+", "") for c in moves]
            game += moves
        else:
            if len(game) >= 6:
                if game.count("*") > 0:
                    game = []
                else:
                    ofile.write(' '.join(game[:14]) + "\n")
                    game = []

    if len(game) >= 6:
        if game.count("*") > 0:
            game = []
        else:
            ofile.write(' '.join(game[:14]))
            game = []
