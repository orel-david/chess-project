from cython cimport int, long

from piece cimport PieceType
from board cimport Board

cdef class Move:
    """
    This class represent a move in the game with origin, target, castling and promotion data
    """
    # instance attributes
    cdef public unsigned long cell
    cdef public unsigned long target
    cdef public unsigned long enemy_cell
    cdef public unsigned long prev_en_passant
    cdef public bint castle
    cdef public bint is_king_side
    cdef public bint is_en_passant
    cdef public PieceType promotion
    cdef public PieceType enemy_type
    cdef public unicode prev_castling
    cdef public int prev_count

    # class methods
    cpdef void set_castle(self, bint is_king_side)
    cpdef void set_promotion(self, PieceType piece)

cpdef bint is_pseudo_legal(Board board, Move move)
cpdef bint is_threatened(Board board, bint is_white, unsigned long cell)
cpdef list get_all_legal_moves(Board board, unsigned long cell, PieceType piece, bint is_white)
cpdef bint condition(Board board, Move move, PieceType piece, bint is_white)
cpdef list get_threats(Board board)
cpdef bint is_under_check(Board board)
cpdef bint is_mate(Board board, bint is_white)
cpdef bint can_castle(Board board, bint is_white, Move move)
cpdef void castle(Board board, bint is_white, Move move, bint valid=*)
cpdef void promote(Board board, Move move)
cpdef void make_move(Board board, Move move, bint valid=*)
cpdef list get_castle_moves(Board board, bint is_white)
cpdef list get_promotion_moves(Move move)
cpdef bint check_stalemate(Board board)
cpdef void fill_undo_info(Board board, Move move, PieceType enemy_type)
cpdef void update_castling_option(unsigned long rook_cell, Board board, bint is_white)
cpdef void undo_move(Board board, Move move)