from mask_utils cimport Masks
from piece cimport PieceType

cdef class Board:
    """

    This is The class that represents the game board and the values regarding it's current state.

    """
    # static attributes
    cdef dict pieces_dict
    cdef list pawn_moves
    cdef list knight_moves
    cdef list king_moves
    cdef list vertical_distances
    cdef Masks masker
    cdef list directions

    # instance attributes
    cdef public unicode castling_options
    cdef public bint is_white
    cdef public unsigned long en_passant_ready
    cdef public int count
    cdef public unsigned long long board
    cdef unsigned long long white_board
    cdef unsigned long long black_board
    cdef unsigned long long sliding
    cdef unsigned long long sliding_attacks
    cdef public unsigned long long[2] attackers
    cdef public bint pin_in_position
    cdef public dict attackers_maps
    cdef public unsigned long long pin_map
    cdef public unsigned long long check_map
    cdef public bint position_in_check
    cdef public bint position_in_double_check
    cdef dict piece_maps
    cdef public list threats
    cdef dict black_pieces
    cdef dict white_pieces

    # class methods
    cpdef unsigned long long get_board(self)
    cpdef bint is_cell_empty(self, unsigned long cell)
    cpdef bint is_cell_colored(self, unsigned long cell, bint is_white)
    cpdef void set_cell_piece(self, unsigned long cell, PieceType piece, bint is_white)
    cpdef void remove_cell_piece(self, unsigned long cell, PieceType piece, bint is_white)
    cpdef dict get_pieces_dict(self, bint is_white)
    cpdef bint is_insufficient(self)
    cpdef bint is_type_of(self, unsigned long cell, PieceType piece)
    cpdef PieceType get_cell_type(self, unsigned long cell)
    cpdef bint __is_safe_en_passant__(self, unsigned long pawn_cell, unsigned long enemy_cell, bint is_white)
    cpdef unsigned long long get_pawn_captures(self, unsigned long cell, bint is_white)
    cpdef unsigned long long get_pawn_moves(self, unsigned long cell, bint is_white)
    cpdef unsigned long long get_king_cell_moves(self, unsigned long cell, bint is_white)
    cpdef unsigned long long get_knight_cell_moves(self, unsigned long cell, bint is_white)
    cpdef unsigned long long get_vertical_cell_moves(self, unsigned long cell, PieceType piece, bint is_white, bint for_attacks=*)
    cpdef unsigned long long get_moves_by_piece(self, unsigned long cell, bint is_white, PieceType piece, bint for_attacks=*)
    cpdef unsigned long long get_moves_by_cell(self, unsigned long cell, bint is_white, bint for_attacks=*)
    cpdef void __update_attacker__(self, bint is_white)
    cpdef unsigned long long get_attacks(self, bint is_white)
    cpdef void __update_pins_and_checks__(self, bint is_white)
    cpdef bint is_pinned(self, unsigned long cell)
    cpdef void update_round(self, unsigned long target_cell, PieceType piece, bint enables_en_passant=*)