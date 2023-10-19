from cython cimport int, long

cdef class Masks:
    """

    This class holds the masks for the lines on the board for move generation

    """
    cdef unsigned long long[8] rank_masks
    cdef unsigned long long[8] files_masks
    cdef unsigned long long[15] diagonal_masks
    cdef unsigned long long[15] anti_diagonal_masks
    cpdef unsigned long long get_rank_mask(self, int rank)
    cpdef unsigned long long get_file_mask(self, int file)
    cpdef unsigned long long get_diagonal_mask(self, int rank, int file, bint is_anti_diagonal)