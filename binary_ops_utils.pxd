from typing import Tuple, List

from mask_utils cimport Masks
from cython cimport int, tuple, long

cdef unsigned long long base

cdef unsigned long long switch_bit(unsigned long long source, unsigned long long row, unsigned long long col, bint on)
cdef unsigned long long switch_cell_bit(unsigned long long source, unsigned long cell, bint on)
cpdef long translate_row_col_to_cell(long row, long col)
cpdef tuple[unsigned long,unsigned long] translate_cell_to_row_col(unsigned long cell)
cdef long get_direction(unsigned long cell, unsigned long target)
cdef unsigned long ms1b_value(unsigned long num)
cdef unsigned long long bit_scan_reverse(unsigned long long val)
cdef unsigned long long outer_cell(unsigned long long cell)
cdef unsigned long long outer_cell_file(unsigned long long cell)
cdef unsigned long long get_bishop_moves(unsigned long long board, unsigned long bishop_cell, Masks masker)
cdef unsigned long long get_rook_moves(unsigned long long board, unsigned long rook_cell, Masks masker)
cdef unsigned long long get_queen_moves(unsigned long long board, unsigned long queen_cell, Masks masker)
cdef list get_turned_bits(word)

