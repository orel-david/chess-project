# cython: language_level=3
# cython: profile=True
from cython cimport int, long

cdef unsigned long long base
base = 1

cdef class Masks:
    """

    This class holds the masks for the lines on the board for move generation

    """

    def __cinit__(self):
        cdef unsigned long long first_file, first_rank, tmp_anti_diagonal, tmp_diagonal, i, j
        first_file = 0x0101010101010101
        self.files_masks[0] = (first_file)

        first_rank = 0xFF
        self.rank_masks[0] = (first_rank)

        for i in range(1, 8):
            self.rank_masks[i] = (first_rank << (i * 8))
            self.files_masks[i] = (first_file << i)

        for i in range(8):
            tmp_diagonal = 0
            tmp_anti_diagonal = 0
            for j in range(8 - i):
                tmp_diagonal |= base << (i + (9 * j))
                tmp_anti_diagonal |= base << ((56 - (i * 8)) - (7 * j))
            self.diagonal_masks[i] = (tmp_diagonal)
            self.anti_diagonal_masks[i] = (tmp_anti_diagonal)

        for i in range(1, 8):
            tmp_diagonal = 0
            tmp_anti_diagonal = 0
            for j in range(8 - i):
                tmp_diagonal |= base << ((8 * i) + (9 * j))
                tmp_anti_diagonal |= base << (56 + i - (7 * j))
            self.diagonal_masks[7+i] = (tmp_diagonal)
            self.anti_diagonal_masks[7+i] = (tmp_anti_diagonal)

    cdef unsigned long long get_rank_mask(self, int rank):
        """ This returns the mask of a certain rank

        :param rank: the rank on the board
        :return: the mask for rank
        """
        return self.rank_masks[rank]

    cdef unsigned long long get_file_mask(self, int file):
        """ This returns the mask of a certain file

        :param file: the file on the board
        :return: the mask for file
        """
        return self.files_masks[file]

    cdef unsigned long long get_diagonal_mask(self, int rank, int file, bint is_anti_diagonal):
        """ This returns the mask for a certain diagonal line for a certain cell

        :param rank: the rank of the cell
        :param file: the file of the cell
        :param is_anti_diagonal: whether we want the diagonal or anti diagonal line
        :return: the mask of the cell's diagonal
        """
        cdef int diff

        if is_anti_diagonal:
            diff = file - 7 + rank
            if diff == 0:
                return self.anti_diagonal_masks[0]
            if diff < 0:
                return self.anti_diagonal_masks[abs(diff)]
            return self.anti_diagonal_masks[7 + diff]
        else:
            diff = file - rank
            if diff == 0:
                return self.diagonal_masks[0]
            if diff > 0:
                return self.diagonal_masks[diff]
            return self.diagonal_masks[7 - diff]
