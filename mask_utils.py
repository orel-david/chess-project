from functools import lru_cache


class Masks:
    """

    This class holds the masks for the lines on the board for move generation

    """
    rank_masks = []
    files_masks = []
    diagonal_masks = []
    anti_diagonal_masks = []

    def __init__(self):

        first_file = 0x0101010101010101
        self.files_masks.append(first_file)

        first_rank = 0xFF
        self.rank_masks.append(first_rank)

        for i in range(1, 8):
            self.rank_masks.append(first_rank << (i * 8))
            self.files_masks.append(first_file << i)

        for i in range(8):
            tmp_diagonal = 0
            tmp_anti_diagonal = 0
            for j in range(8 - i):
                tmp_diagonal |= 1 << (i + (9 * j))
                tmp_anti_diagonal |= 1 << ((56 - (i * 8)) - (7 * j))
            self.diagonal_masks.append(tmp_diagonal)
            self.anti_diagonal_masks.append(tmp_anti_diagonal)

        for i in range(1, 8):
            tmp_diagonal = 0
            tmp_anti_diagonal = 0
            for j in range(8 - i):
                tmp_diagonal |= 1 << ((8 * i) + (9 * j))
                tmp_anti_diagonal |= 1 << (56 + i - (7 * j))
            self.diagonal_masks.append(tmp_diagonal)
            self.anti_diagonal_masks.append(tmp_anti_diagonal)

    def get_rank_mask(self, rank: int) -> int:
        """ This returns the mask of a certain rank

        :param rank: the rank on the board
        :return: the mask for rank
        """
        return self.rank_masks[rank]

    def get_file_mask(self, file: int) -> int:
        """ This returns the mask of a certain file

        :param file: the file on the board
        :return: the mask for file
        """
        return self.files_masks[file]

    @lru_cache(maxsize=128)
    def get_diagonal_mask(self, rank: int, file: int, is_anti_diagonal: bool) -> int:
        """ This returns the mask for a certain diagonal line for a certain cell

        :param rank: the rank of the cell
        :param file: the file of the cell
        :param is_anti_diagonal: whether we want the diagonal or anti diagonal line
        :return: the mask of the cell's diagonal
        """
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
