#cython: language_level=3

from typing import Tuple, List

from mask_utils cimport Masks
from cython cimport int, tuple, long

cdef unsigned long long base
base = 1

cpdef unsigned long long switch_bit(unsigned long long source, unsigned long long row, unsigned long long col, bint on):
    """
    Turn on or off 1 bit in the cell coordinates.

    :param source: The original bit sequence
    :param row: The cell row
    :param col: The cell column
    :param on: The boolean that says whether to turn the bit on or off
    :return: The modified int
    """
    cdef unsigned long long cell
    cell = row * 8
    cell += col
    if on:
        return source | (base << (cell))
    return source & (~(base << (cell)))


cpdef unsigned long long switch_cell_bit(unsigned long long source, unsigned long cell, bint on):
    """ Turn on or off 1 bit in the cell index.

    :param source: The original bit sequence
    :param cell: The cell index
    :param on: The boolean that says whether to turn the bit on or off
    :return: The modified int
    """

    if on:
        return source | (base << cell)
    return source & (~(base << cell))


cpdef long translate_row_col_to_cell(long row, long col):
    """ This method is used to convert cell coordinates to cell index.

    :param row: The cell row
    :param col: The cell column
    :return: The cell index
    """

    if row > 8 or col > 8 or row < 1 or col < 1:
        return -1

    row = row - 1
    col = col - 1
    return row * 8 + col


cpdef tuple[unsigned long,unsigned long] translate_cell_to_row_col(unsigned long cell):
    """ This method convert given cell index to a row and a column.

    :param cell: The cell index
    :return: A tuple of the cell row and column
    """

    return (<int>(cell / 8), cell % 8)


def get_turned_bits(word):
    """ This method gets a byte word as an int and returns the bits that are on.

    :param word: The integer we inspect
    :return: A list of the indexes which their corresponding bit is on
    """

    result = []
    temp = word
    curr = 0
    while temp != 0:
        if temp & 1:
            result.append(curr)
        temp = temp >> 1
        curr += 1
    return result


cpdef unsigned long get_direction(unsigned long cell, unsigned long target):
    """ This method return the direction between two cell, if they aren't in a line it returns 0.

    :param cell: The first cell
    :param target: The second cell
    :return: A direction value according to the directions in board or 0 if not on a line.
    """
    cdef unsigned long target_col, target_row, cell_col, cell_row , row_diff, col_diff

    target_row, target_col = translate_cell_to_row_col(target)
    cell_row, cell_col = translate_cell_to_row_col(cell)
    row_diff = target_row - cell_row
    col_diff = target_col - cell_col
    if col_diff == 0:
        return 8 if row_diff > 0 else -8

    if row_diff == 0:
        return 1 if col_diff > 8 else -1

    if row_diff == col_diff:
        return 9 if row_diff > 0 else -9

    if row_diff == -col_diff:
        return -7 if row_diff < 0 else 7

    return 0


cdef unsigned long ms1b_value(unsigned long num):
    """ This returns the most significant bit for a certain 1 byte number

    :param num: the number
    :return: the index of the most significant bit
    """
    return (
        7 if num > 127 else
        6 if num > 63 else
        5 if num > 31 else
        4 if num > 15 else
        3 if num > 7 else
        2 if num > 3 else
        1 if num > 1 else
        0
    )


cdef unsigned long long bit_scan_reverse(unsigned long long val):
    """ This function returns the MSB for a certain 64 bit int

    :param val: the number
    :return: the index of the msb
    """
    cdef unsigned long long result
    if val == 0:
        return 0

    result = 0
    if val > 0xFFFFFFFF:
        val >>= 32
        result += 32
    if val > 0xFFFF:
        val >>= 16
        result += 16
    if val > 0xff:
        val >>= 8
        result += 8

    return ms1b_value(val) + result


cdef unsigned long long outer_cell(unsigned long long cell):
    """ This function provides a msk for certain edge cases in the move generation

    :param cell: the cell of the piece
    :return: the mask for the relevant cell
    """
    cdef unsigned long long origin
    origin = 0x81
    return (origin << (cell & 56)) & ~(base << cell)


cdef unsigned long long outer_cell_file(unsigned long long cell):
    """ This function provides a msk for certain edge cases in the move generation

    :param cell: the cell of the piece
    :return: the mask for the relevant cell
    """
    return (0x0100000000000001 << (cell & 7)) & (~(base << cell))


cpdef unsigned long long get_bishop_moves(unsigned long long board, unsigned long bishop_cell, Masks masker):
    """ This method is using SBAMG algorithm to generate the bishop's moves

    :param board: bitboard of the current gameboard
    :param bishop_cell: the index of the bishop's cell
    :param masker: a Masks object for diagonals' masks
    :return: a mask of the pseudo legal bishop's moves
    """
    cdef unsigned long long rank, file, mask, occ, negative_ray, bsq, cbn, result
    rank, file = translate_cell_to_row_col(bishop_cell)

    mask = masker.get_diagonal_mask(rank, file, True)
    occ = (board & mask)
    occ ^= (base << bishop_cell)
    negative_ray = occ & ((base << bishop_cell) - 1)
    bsq = bit_scan_reverse(negative_ray)
    cbn = (((base * 3) ^ ((negative_ray == 0) << 1)) << bsq)
    occ = occ ^ (occ - cbn)
    result = occ & mask

    mask = masker.get_diagonal_mask(rank, file, False)
    occ = (board & mask)
    occ ^= (base << bishop_cell)
    negative_ray = occ & ((base << bishop_cell) - 1)
    bsq = bit_scan_reverse(negative_ray)
    cbn = (((base * 3) ^ ((negative_ray == 0) << 1)) << bsq)
    occ = occ ^ (occ - cbn)
    result |= occ & mask

    return result


cpdef unsigned long long get_rook_moves(unsigned long long board, unsigned long rook_cell, Masks masker):
    """ This method is using SBAMG algorithm to generate the rook's moves

    :param board: bitboard of the current gameboard
    :param rook_cell: the index of the rook's cell
    :param masker: a Masks object for diagonals' masks
    :return: a mask of the pseudo legal rook's moves
    """
    cdef unsigned long long rank, file, mask, occ, bsq, cbn, result

    rank, file = translate_cell_to_row_col(rook_cell)

    mask = masker.get_rank_mask(rank)
    occ = (board & mask) | outer_cell(rook_cell)
    occ ^= (base << rook_cell)
    bsq = bit_scan_reverse(occ & ((base << rook_cell) - 1))
    cbn = (3 * base) << bsq if rook_cell != 0 else 1
    occ = occ ^ (occ - cbn)
    result = occ & mask

    mask = masker.get_file_mask(file)
    occ = (board & mask) | outer_cell_file(rook_cell)
    occ ^= (base << rook_cell)
    bsq = bit_scan_reverse(occ & ((base << rook_cell) - 1))
    cbn = (3 * base) << bsq
    occ = occ ^ (occ - cbn)
    result |= occ & mask

    return result


cpdef unsigned long long get_queen_moves(unsigned long long board, unsigned long queen_cell, Masks masker):
    """ This method is using SBAMG algorithm to generate the queen's moves

    :param board: bitboard of the current gameboard
    :param queen_cell: the index of the queen's cell
    :param masker: a Masks object for diagonals' masks
    :return: a mask of the pseudo legal queen's moves
    """
    return get_rook_moves(board, queen_cell, masker) | get_bishop_moves(board, queen_cell, masker)
