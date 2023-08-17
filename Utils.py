from board import Board
from cell import Cell
from chess_exceptions import NonLegal, KingUnderCheck, KingNonLegal, KingSacrifice
from pieces.piece import PieceType, Piece


class Move:
    row: int
    col: int
    castle: bool
    is_king_side: bool

    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.castle = False
        self.is_king_side = False

    def set_castle(self, is_right):
        self.castle = True
        self.is_king_side = is_right


def en_passant_check(board: Board, pawn, row: int, col: int):
    cell = board.get_cell(row, col)
    if cell is None:
        return False

    if cell.is_empty():
        return False
    if (cell.is_white() ^ pawn.is_white()) and (
            cell.get_cell_type() == PieceType.PAWN):
        return True if cell.en_passant else False


def validate_move(board: Board, cell, move):
    eat = (board.get_cell(move.row, move.col).is_white() ^ cell.is_white())
    free = board.get_cell(move.row, move.col).is_empty()
    return (not (board.get_cell(move.row, move.col) is None)) and (free or eat)


def get_line_moves(board: Board, cell: Cell, directions):
    moves = []
    cell_row = cell.get_row()
    cell_col = cell.get_col()
    for direction in directions:
        i = 1
        temp = Move(cell_row + direction[0], cell_col + direction[1])
        while validate_move(board, cell, temp):
            moves.append(temp)
            i += 1
            temp = Move(cell_row + direction[0] * i, cell_col + direction[1] * i)
    return moves


def get_pawn_moves(board: Board, cell: Cell):
    if cell.get_cell_type() != PieceType.PAWN:
        return []
    pawn_advancement = 1 if cell.is_white() else -1
    cell_row = cell.get_row()
    cell_col = cell.get_col()
    moves = []
    if board.get_cell(cell_row + pawn_advancement, cell_col).is_empty():
        moves.append(Move(cell_row + pawn_advancement, cell_col))
        if cell.cell_piece.start and board.get_cell(cell_row + 2 * pawn_advancement, cell_col).is_empty():
            moves.append(Move(cell_row + 2 * pawn_advancement, cell_col))

    moves += filter(lambda move: (not (board.get_cell(move.row, move.col) is None)) and (
            board.get_cell(move.row, move.col).is_white() ^ cell.is_white() and (
        not board.get_cell(move.row, move.col).is_empty())),
                    [Move(cell_row + pawn_advancement, cell_col() + 1),
                     Move(cell_row() + pawn_advancement, cell_col() - 1)])

    moves += filter(lambda move: en_passant_check(board, cell.cell_piece, move.row, move.col),
                    [Move(cell_row(), cell_col() + 1),
                     Move(cell_row(), cell_col() - 1)])

    return list(moves)


def get_knight_moves(board: Board, cell: Cell):
    if cell.get_cell_type() != PieceType.KNIGHT:
        return []
    cell_row = cell.get_row()
    cell_col = cell.get_col()
    moves = list(map(lambda m: Move(cell_row + m[0], cell_col + m[1]), cell.get_cell_piece().get_moves()))
    moves = filter(lambda move: validate_move(board, cell, move), moves)
    return list(moves)


def get_king_moves(board: Board, cell: Cell):
    if cell.get_cell_type() != PieceType.KING:
        return []
    cell_row = cell.get_row()
    cell_col = cell.get_col()
    moves = list(map(lambda m: Move(cell_row + m[0], cell_col + m[1]), cell.get_cell_piece().get_moves()))
    moves = filter(lambda move: validate_move(board, cell, move), moves)
    # Castling would be handled differently
    return list(moves)


def get_rook_moves(board: Board, cell: Cell):
    if cell.get_cell_type() != PieceType.ROOK:
        return []
    return get_line_moves(board, cell, cell.get_cell_piece().get_moves())


def get_queen_moves(board: Board, cell: Cell):
    if cell.get_cell_type() != PieceType.QUEEN:
        return []
    return get_line_moves(board, cell, cell.get_cell_piece().get_moves())


def get_bishop_moves(board: Board, cell: Cell):
    if cell.get_cell_type() != PieceType.BISHOP:
        return []
    return get_line_moves(board, cell, cell.get_cell_piece().get_moves())


moves_dict = {
    PieceType.PAWN: get_pawn_moves,
    PieceType.KNIGHT: get_knight_moves,
    PieceType.KING: get_king_moves,
    PieceType.ROOK: get_rook_moves,
    PieceType.QUEEN: get_queen_moves,
    PieceType.BISHOP: get_bishop_moves,
    PieceType.EMPTY: lambda b, c: []
}


def get_all_normal_moves(board: Board, cell: Cell):
    # And en passant moves
    piece_type = cell.get_cell_type()
    return moves_dict[piece_type](board, cell)


def is_legal(board: Board, cell: Cell, move: Move):
    return move in get_all_normal_moves(board, cell)


def is_threatened(board: Board, is_white: bool, cell: Cell):
    enemy_pieces = board.get_pieces_dict(not is_white)
    for piece in enemy_pieces:
        for enemy in piece:
            if is_legal(board, enemy, Move(cell.get_row(), cell.get_col())):
                return False
    return True


def is_under_check(board: Board, is_white: bool):
    king_cell = board.get_pieces_dict(is_white)[PieceType.KING][0]
    return is_threatened(board, is_white, king_cell)


def castle(board: Board, is_white: bool, move: Move):
    if move.castle is False:
        return

    row = 1 if is_white else 8
    col = 8 if move.is_king_side else 1
    king_cell = board.get_pieces_dict(is_white)[PieceType.KING][0]
    king = king_cell.get_cell_piece()
    rook_cell = board.get_cell(row, col)
    rook = rook_cell.get_cell_piece()
    if king.moved or rook_cell.get_cell_type() != PieceType.ROOK or rook.moved:
        return

    direction = 1 if move.is_king_side else -1
    moves = [Move(row, 5 + direction), Move(row, 5 + 2 * direction)]
    cond = (lambda m: board.get_cell(m.row, m.col).is_empty() and (
        not is_threatened(board, is_white, board.get_cell(m.row, m.col))))
    legal = all(cond(m) for m in moves)
    if legal:
        king_cell.cell_piece = Piece(False)
        rook_cell.cell_piece = Piece(False)
        king.moved = True
        rook.moved = True
        board.get_cell(row, moves[1].col).cell_piece = king
        board.get_cell(row, moves[0].col).cell_piece = rook
        pieces_dict = board.get_pieces_dict(is_white)
        pieces_dict[PieceType.KING] = board.get_cell(row, moves[1].col)
        pieces_dict[PieceType.ROOK] = [board.get_cell(row, moves[0].col) if c == rook_cell else c for c in
                                       pieces_dict[PieceType.ROOK]]


def check_protect(board: Board, cell: Cell):
    if cell.get_cell_type() == PieceType.KING:
        return True

    piece = cell.get_cell_piece()
    cell.cell_piece = Piece(False)
    result = is_under_check(board, piece.is_white())
    cell.cell_piece = piece
    return result


def update_en_passant(board: Board):
    if board.en_passant_ready is not None:
        board.en_passant_ready.en_passant = False
        board.en_passant_ready = None


def update_piece(board: Board, cell: Cell, move: Move):
    if cell.get_cell_type() == PieceType.KING or cell.get_cell_type() == PieceType.ROOK:
        cell.get_cell_piece().moved = True

    if cell.get_cell_type() == PieceType.PAWN:
        pawn = cell.get_cell_piece()
        pawn.start = False
        pawn.en_passant = True if abs(cell.get_row() - move.row) == 2 else False
        if pawn.en_passant:
            board.en_passant_ready = pawn


def make_move(board: Board, cell: Cell, move: Move):
    if move.castle:
        castle(board, cell.is_white(), move)

    # TODO: ADD PROMOTION CASE

    if not is_legal(board, cell, move):
        raise NonLegal()

    if is_under_check(board, cell.is_white()):
        if cell.get_cell_type() != PieceType.KING:
            raise KingUnderCheck()

    if cell.get_cell_type() == PieceType.KING:
        if is_threatened(board, cell.is_white(), board.get_cell(move.row, move.col)):
            raise KingNonLegal()

    if check_protect(board, cell):
        raise KingSacrifice()

    target_cell = board.get_cell(move.row, move.col)
    if target_cell.get_cell_type() != PieceType.EMPTY:
        pieces_dict = board.get_pieces_dict(target_cell.is_white())
        pieces_dict[cell.get_cell_type()].remove(target_cell)

    pieces_dict = board.get_pieces_dict(cell.is_white())
    pieces_dict[PieceType.ROOK] = [target_cell if c == cell else c for c in
                                   pieces_dict[cell.get_cell_type()]]
    target_cell.cell_piece = cell.get_cell_piece()
    cell.cell_piece = Piece(False)
    update_en_passant(board)
    update_piece(board, cell, move)


def translate_algebraic_notation_move(notation: str):
    if notation.lower() == "o-o":
        move = Move(0, 0)
        move.set_castle(True)
        return move

    if notation.lower() == "o-o-o":
        move = Move(0, 0)
        move.set_castle(False)
        return move
    # TODO: ADD PROMOTION CASE

    return Move(int(notation[1]), ord(notation[0].lower()) - ord('a') + 1)
