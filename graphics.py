import pygame
from board import Board
from pieces.piece import PieceType


def create_image_dict(is_white: bool, width: int, height: int):
    color = "white" if is_white else "black"
    pieces = {PieceType.PAWN: "pawn", PieceType.QUEEN: "queen", PieceType.BISHOP: "bishop",
              PieceType.KNIGHT: "knight",
              PieceType.KING: "king", PieceType.ROOK: "rook"}
    output_dict = {}
    for piece in pieces.keys():
        img = pygame.image.load("images/{} {}.png".format(color, pieces[piece]))
        img = pygame.transform.scale(img, (width / 8, height / 8))
        output_dict[piece] = img
    return output_dict


class GUI:
    width = 800
    height = 800
    white_pieces = create_image_dict(True, width, height)
    black_pieces = create_image_dict(False, width, height)
    pieces = {True: white_pieces, False: black_pieces}

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Chess game")
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.board_image = pygame.image.load("images/empty-board.png")
        self.board_image = pygame.transform.scale(self.board_image, (self.width, self.height))
        self.screen.blit(self.board_image, (0, 0))
        pygame.display.flip()

    def draw_at_cell(self, img, row: int, col: int):
        if row > 8 or col > 8 or row < 1 or col < 1:
            return
        self.screen.blit(img, ((8 - col) * (self.width / 8), (8 - row) * (self.height / 8)))

    def draw_board(self, board: Board):
        self.screen.blit(self.board_image, (0, 0))
        for color in self.pieces.keys():
            pieces_dict = board.get_pieces_dict(color)
            for piece in pieces_dict.keys():
                for cell in pieces_dict[piece]:
                    self.draw_at_cell(self.pieces[color][cell.get_cell_type()], cell.get_row(), cell.get_col())
        pygame.display.flip()

    def handle_events(self, board: Board):
        pass

    def draw_moves(self, board: Board):
        pass

    def mark_checks(self, board: Board):
        pass
