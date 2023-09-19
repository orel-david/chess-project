# chess-project
## Overview
Personal project to create a working chess game with graphical interface in python for learning purposes
## Board
The board is the main data structure of the project. 
The board uses bitmaps to represent the current position of the board, in addition to that it also holds two dictionaries to map piece to the cells where it's in,
based on piece color.
### features
* Import position from Forsyth–Edwards Notation (FEN)
* Maintaining maps of attacks for each piece type by player
* Maintain a map of all the pinned pieces
* Set/remove piece from a cell
* Get all pseudo-legal moves from a cell
### Intended upgrades
* Optimization to generation of vertical moves
* Optimization to the update of the attacks' maps
## Graphics
This is the interface with the player, through the GUI the player tells which piece he wants to move and where. The module being used for this is pygame
### features
* Marking all legal moves on the board
* Marking the pieces that threatens the king
* Marking capture moves
### Intended upgrades
* Switching the board image to an image that fits the board better
## Installation
To run the chess game, you'll need Python 3.7 or higher. Follow these steps:

1. Clone the repository: `git clone https://github.com/orel-david/chess-project.git`
2. Navigate to the project folder: `cd chess-project`
3. Install the required dependencies: `pip install pygame`
4. Run `gui_game.py` to play the game

## Attributions
<a href="https://www.flaticon.com/free-icons/chess" title="chess icons">Chess icons created by deemakdaksina - Flaticon</a>