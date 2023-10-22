# chess-project
## Overview
Personal project to create a working chess game with graphical interface in python for learning purposes
## Core module
The core module groups the functions and classes required for the logics of the game.
Due to performance reasons the majority of the files in that module are written  with cython.
The files were compiled using `python setup.py build_ext --inplace` and there is no need to recompile them.
### Core submodules
Each one of the following submodules is made out of three file.
The first one is `.pxd` file which serves as a header file, a `.pyx` file which contains the implementation and a `.pyd` which is the compilation's result.
* `mask_utils` - This submodule is used to get a bit mask for each rank, file, diagonal and anti-diagonal.
* `binary_ops_utils` - This submodule contains mainly helper function for bit operations and generating moves for the sliding pieces.
* `piece` - Holds an enum for all the piece types in the game including empty cell.
* `board` - This submodule includes the `Board` class which is the main data structure of the game.
* `core_utils` - Holds general helper function to make or unmake a move and to check if there is a mate or a stalemate.
## Board
The board is the main data structure of the project. 
The board uses bitmaps to represent the current position of the board, in addition to that it also holds two dictionaries to map piece to the cells where it's in,
based on piece color.
### Features
* Import position from Forsyth–Edwards Notation (FEN)
* Maintaining maps of attacks for each piece type by player
* Maintain a map of all the pinned pieces
* Set/remove piece from a cell
* Get all pseudo-legal moves from a cell
## Graphics
This is the interface with the player, through the GUI the player tells which piece he wants to move and where. The module being used for this is pygame
### Features
* Marking all legal moves on the board
* Marking the pieces that threatens the king
* Marking capture moves
## Installation
To run the chess game, you'll need Python 3.7 or higher. Follow these steps:

1. Clone the repository: `git clone https://github.com/orel-david/chess-project.git`
2. Navigate to the project folder: `cd chess-project`
3. Install the required dependencies: `pip install pygame`
4. Run `gui_game.py` to play the game

## Attributions
<a href="https://www.flaticon.com/free-icons/chess" title="chess icons">Chess icons created by deemakdaksina - Flaticon</a>