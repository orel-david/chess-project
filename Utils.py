import pieces.rook
from board import Board
from cell import Cell
from chess_exceptions import NonLegal, KingUnderCheck, KingNonLegal, KingSacrifice
from pieces.piece import PieceType, Piece
import pieces


class Move:
    row: int
    col: int
    castle: bool
    is_king_side: bool
    is_en_passant: bool
    promotion: PieceType

    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.castle = False
        self.is_king_side = False
        self.is_en_passant = False
        self.promotion = PieceType.EMPTY

    def set_castle(self, is_right):
        self.castle = True
        self.is_king_side = is_right

    def set_promotion(self, piece):
        self.promotion = piece


def en_passant_check(board: Board, pawn, row: int, col: int):
    cell = board.get_cell(row, col)
    if cell is None:
        return False

    if cell.is_empty():
        return False
    if (cell.is_white() ^ pawn.is_white()) and (
            cell.get_cell_type() == PieceType.PAWN):
        return True if cell.get_cell_piece().en_passant else False


def validate_move(board: Board, cell, move):
    if board.get_cell(move.row, move.col) is None:
        return False
    eat = (board.get_cell(move.row, move.col).is_white() ^ cell.is_white())
    free = board.get_cell(move.row, move.col).is_empty()
    return free or eat


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
            if board.get_cell(temp.row, temp.col).get_cell_type() != PieceType.EMPTY:
                break
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
                    [Move(cell_row + pawn_advancement, cell_col + 1),
                     Move(cell_row + pawn_advancement, cell_col - 1)])

    en_passant_moves = [Move(cell_row + pawn_advancement, cell_col + 1),
                        Move(cell_row + pawn_advancement, cell_col - 1)]

    for m in en_passant_moves:
        m.is_en_passant = True

    moves += filter(lambda move: en_passant_check(board, cell.cell_piece, move.row - pawn_advancement, move.col),
                    en_passant_moves)

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
    moves = get_all_normal_moves(board, cell)
    for m in moves:
        if m.row == move.row and move.col == m.col:
            move.is_en_passant = m.is_en_passant
            return True
    return False


def is_threatened(board: Board, is_white: bool, cell: Cell):
    enemy_pieces = board.get_pieces_dict(not is_white)
    for piece in enemy_pieces:
        for enemy in enemy_pieces[piece]:
            if is_legal(board, enemy, Move(cell.get_row(), cell.get_col())) and cell.is_white() == is_white:
                return True
    return False


def get_threats(board: Board, is_white: bool, cell: Cell):
    threats = []
    enemy_pieces = board.get_pieces_dict(not is_white)
    for piece in enemy_pieces:
        for enemy in enemy_pieces[piece]:
            if is_legal(board, enemy, Move(cell.get_row(), cell.get_col())) and cell.is_white() == is_white:
                threats.append(enemy)
    return threats


def is_under_check(board: Board, is_white: bool):
    king_cell = board.get_pieces_dict(is_white)[PieceType.KING][0]
    return is_threatened(board, is_white, king_cell)


def is_mate(board: Board, is_white: bool):
    if not is_under_check(board, is_white):
        return False
    piece_dict = board.get_pieces_dict(is_white)
    enemy_dict = board.get_pieces_dict(not is_white)
    king_cell = piece_dict[PieceType.KING][0]
    # Add case for defending piece
    for piece in piece_dict.keys():
        for cell in piece_dict[piece]:
            block_moves = get_all_normal_moves(board, cell)
            for move in block_moves:
                curr_cell = board.get_cell(move.row, move.col)
                prev_piece = curr_cell.get_cell_piece()
                curr_cell.cell_piece = cell.cell_piece
                cell.cell_piece = Piece(False)
                if curr_cell.get_cell_type() == PieceType.KING:
                    piece_dict[PieceType.KING] = [curr_cell]
                if prev_piece.piece_type != PieceType.EMPTY:
                    enemy_dict[prev_piece.piece_type] = [c for c in enemy_dict[prev_piece.piece_type] if
                                                         c != curr_cell]
                result = is_under_check(board, is_white)
                if prev_piece.piece_type != PieceType.EMPTY:
                    enemy_dict[prev_piece.piece_type].append(curr_cell)
                piece_dict[PieceType.KING] = [king_cell]
                cell.cell_piece = curr_cell.cell_piece
                curr_cell.cell_piece = prev_piece
                if not result:
                    return False

    return True


def can_castle(board: Board, is_white: bool, move: Move):
    if move.castle is False:
        return False
    if is_under_check(board, is_white):
        return False

    row = 1 if is_white else 8
    col = 8 if move.is_king_side else 1
    king_cell = board.get_pieces_dict(is_white)[PieceType.KING][0]
    king = king_cell.get_cell_piece()
    rook_cell = board.get_cell(row, col)
    rook = rook_cell.get_cell_piece()
    if king.moved or rook_cell.get_cell_type() != PieceType.ROOK or rook.moved:
        return False

    direction = 1 if move.is_king_side else -1
    moves = [Move(row, 5 + direction), Move(row, 5 + 2 * direction)]
    cond = (lambda m: board.get_cell(m.row, m.col).is_empty() and (
        not is_threatened(board, is_white, board.get_cell(m.row, m.col))))
    return all(cond(m) for m in moves)


def castle(board: Board, is_white: bool, move: Move):
    if move.castle is False:
        raise NonLegal()
    if is_under_check(board, is_white):
        raise KingUnderCheck()

    row = 1 if is_white else 8
    col = 8 if move.is_king_side else 1
    king_cell = board.get_pieces_dict(is_white)[PieceType.KING][0]
    king = king_cell.get_cell_piece()
    rook_cell = board.get_cell(row, col)
    rook = rook_cell.get_cell_piece()
    if king.moved or rook_cell.get_cell_type() != PieceType.ROOK or rook.moved:
        raise NonLegal()

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
        pieces_dict[PieceType.KING] = [board.get_cell(row, moves[1].col)]
        pieces_dict[PieceType.ROOK] = [board.get_cell(row, moves[0].col) if c == rook_cell else c for c in
                                       pieces_dict[PieceType.ROOK]]


def update_en_passant(board: Board, cell: Cell, move: Move):
    if move.is_en_passant:
        pawn_advancement = 1 if cell.is_white() else -1
        enemy = board.get_cell(move.row - pawn_advancement, move.col)
        enemy.cell_piece = Piece(False)
        enemy_dict = board.get_pieces_dict(not cell.is_white())
        enemy_dict[PieceType.PAWN] = [c for c in enemy_dict[PieceType.PAWN] if c != enemy]
    if board.en_passant_ready is not None:
        board.en_passant_ready.en_passant = False
        board.en_passant_ready = None


def update_piece(board: Board, cell: Cell, move: Move, origin_cell: Cell):
    if cell.get_cell_type() == PieceType.KING or cell.get_cell_type() == PieceType.ROOK:
        cell.get_cell_piece().moved = True

    if cell.get_cell_type() == PieceType.PAWN:
        board.count = 0
        pawn = cell.get_cell_piece()
        pawn.start = False
        pawn.en_passant = True if abs(origin_cell.get_row() - move.row) == 2 else False
        if pawn.en_passant:
            board.en_passant_ready = pawn
    board.count = board.count + 1


def promote(board: Board, cell: Cell, move: Move):
    if move.promotion == PieceType.EMPTY:
        raise NonLegal()
    if cell.get_cell_type() != PieceType.PAWN:
        raise NonLegal()

    pieces_dict = board.get_pieces_dict(cell.is_white())
    color = cell.is_white()
    if move.promotion == PieceType.ROOK:
        piece = pieces.rook.Rook(color)
    elif move.promotion == PieceType.BISHOP:
        piece = pieces.bishop.Bishop(color)
    elif move.promotion == PieceType.KNIGHT:
        piece = pieces.knight.Knight(color)
    else:
        piece = pieces.queen.Queen(color)
    cell.cell_piece = piece
    pieces_dict[move.promotion].append(cell)
    pieces_dict[PieceType.PAWN] = [c for c in pieces_dict[PieceType.PAWN] if c != cell]


def check_stops_check(board: Board, cell: Cell, move: Move):
    piece_dict = board.get_pieces_dict(cell.is_white())
    enemy_dict = board.get_pieces_dict(not cell.is_white())
    king_cell = piece_dict[PieceType.KING][0]
    curr_cell = board.get_cell(move.row, move.col)
    prev_piece = curr_cell.get_cell_piece()
    curr_cell.cell_piece = cell.cell_piece
    cell.cell_piece = Piece(False)
    if not curr_cell.is_empty():
        piece_dict[curr_cell.get_cell_type()] = [c if c != cell else curr_cell for
                                                 c in piece_dict[curr_cell.get_cell_type()]]
    if prev_piece.piece_type != PieceType.EMPTY:
        enemy_dict[prev_piece.piece_type] = [c for c in enemy_dict[prev_piece.piece_type] if
                                             c != curr_cell]
    result = is_under_check(board, curr_cell.is_white())
    if prev_piece.piece_type != PieceType.EMPTY:
        enemy_dict[prev_piece.piece_type].append(curr_cell)
    if not curr_cell.is_empty():
        piece_dict[curr_cell.get_cell_type()] = [c if c != curr_cell else cell for
                                                 c in piece_dict[curr_cell.get_cell_type()]]
    piece_dict[PieceType.KING] = [king_cell]
    cell.cell_piece = curr_cell.cell_piece
    curr_cell.cell_piece = prev_piece
    return not result


def make_move(board: Board, cell: Cell, move: Move, valid=False):
    if move.castle:
        castle(board, cell.is_white(), move)

    if not valid:
        if not is_legal(board, cell, move):
            raise NonLegal()

        if is_under_check(board, cell.is_white()):
            if not check_stops_check(board, cell, move):
                raise KingUnderCheck()

        if cell.get_cell_type() == PieceType.KING:
            if is_threatened(board, cell.is_white(), board.get_cell(move.row, move.col)):
                raise KingNonLegal()

        if not check_stops_check(board, cell, move):
            raise KingSacrifice()

    if move.promotion != PieceType.EMPTY:
        promote(board, cell, move)

    target_cell = board.get_cell(move.row, move.col)
    if target_cell.get_cell_type() != PieceType.EMPTY:
        board.count = 0
        pieces_dict = board.get_pieces_dict(target_cell.is_white())
        pieces_dict[target_cell.get_cell_type()] = [c for c in pieces_dict[target_cell.get_cell_type()] if
                                                    c != target_cell]
    pieces_dict = board.get_pieces_dict(cell.is_white())
    pieces_dict[cell.get_cell_type()] = [target_cell if c == cell else c for c in pieces_dict[cell.get_cell_type()]]
    target_cell.cell_piece = cell.get_cell_piece()
    cell.cell_piece = Piece(False)
    update_en_passant(board, target_cell, move)
    update_piece(board, target_cell, move, cell)


def translate_algebraic_notation_move(notation: str):
    pieces_dict = {'q': PieceType.QUEEN, 'r': PieceType.ROOK, 'b': PieceType.BISHOP, 'n': PieceType.KNIGHT}

    if notation.lower() == "o-o":
        move = Move(0, 0)
        move.set_castle(True)
        return move

    if notation.lower() == "o-o-o":
        move = Move(0, 0)
        move.set_castle(False)
        return move

    if len(notation) == 3:
        if notation[0] in pieces_dict.keys():
            move = Move(int(notation[2]), ord(notation[1].lower()) - ord('a') + 1)
            move.set_promotion(pieces_dict[notation[0]])
            return move
        raise NonLegal

    if len(notation) != 2:
        raise NonLegal

    return Move(int(notation[1]), ord(notation[0].lower()) - ord('a') + 1)


def check_stalemate(board: Board):
    if board.count >= 50:
        return True

    return board.is_insufficient()
