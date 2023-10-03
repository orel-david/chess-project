from functools import lru_cache
from typing import Tuple, List

from mask_utils import Masks


def switch_bit(source: int, row: int, col: int, on: bool) -> int:
    """ Turn on or off 1 bit in the cell coordinates.

    :param source: The original bit sequence
    :param row: The cell row
    :param col: The cell column
    :param on: The boolean that says whether to turn the bit on or off
    :return: The modified int
    """

    if on:
        return source | (1 << (row * 8 + col))
    return source & (~(1 << (row * 8 + col)))


def switch_cell_bit(source: int, cell: int, on: bool) -> int:
    """ Turn on or off 1 bit in the cell index.

    :param source: The original bit sequence
    :param cell: The cell index
    :param on: The boolean that says whether to turn the bit on or off
    :return: The modified int
    """

    if on:
        return source | (1 << cell)
    return source & (~(1 << cell))


def translate_row_col_to_cell(row: int, col: int) -> int:
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


def translate_cell_to_row_col(cell: int) -> Tuple[int, int]:
    """ This method convert given cell index to a row and a column.

    :param cell: The cell index
    :return: A tuple of the cell row and column
    """

    return int(cell / 8), cell % 8


def get_turned_bits(word: int) -> List[int]:
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


def get_direction(cell: int, target: int) -> int:
    """ This method return the direction between two cell, if they aren't in a line it returns 0.

    :param cell: The first cell
    :param target: The second cell
    :return: A direction value according to the directions in board or 0 if not on a line.
    """

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


@lru_cache(maxsize=256)
def ms1b_value(num : int) -> int:
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


@lru_cache(maxsize=64)
def bit_scan_reverse(val: int) -> int:
    """ This function returns the MSB for a certain 64 bit int

    :param val: the number
    :return: the index of the msb
    """
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


def outer_cell(cell: int) -> int:
    """ This function provides a msk for certain edge cases in the move generation

    :param cell: the cell of the piece
    :return: the mask for the relevant cell
    """
    return (0x81 << (cell & 56)) & ~(1 << cell)


def outer_cell_file(cell: int) -> int:
    """ This function provides a msk for certain edge cases in the move generation

    :param cell: the cell of the piece
    :return: the mask for the relevant cell
    """
    return (0x0100000000000001 << (cell & 7)) & ~(1 << cell)


def get_bishop_moves(board: int, bishop_cell: int, masker: Masks) -> int:
    """ This method is using SBAMG algorithm to generate the bishop's moves

    :param board: bitboard of the current gameboard
    :param bishop_cell: the index of the bishop's cell
    :param masker: a Masks object for diagonals' masks
    :return: a mask of the pseudo legal bishop's moves
    """
    rank, file = translate_cell_to_row_col(bishop_cell)

    mask = masker.get_diagonal_mask(rank, file, True)
    occ = (board & mask)
    occ ^= (1 << bishop_cell)
    negative_ray = occ & ((1 << bishop_cell) - 1)
    bsq = bit_scan_reverse(negative_ray)
    cbn = 3 << bsq if negative_ray != 0 else 1
    occ = occ ^ (occ - cbn)
    result = occ & mask

    mask = masker.get_diagonal_mask(rank, file, False)
    occ = (board & mask)
    occ ^= (1 << bishop_cell)
    negative_ray = occ & ((1 << bishop_cell) - 1)
    bsq = bit_scan_reverse(negative_ray)
    cbn = 3 << bsq if negative_ray != 0 else 1
    occ = occ ^ (occ - cbn)
    result |= occ & mask

    return result


def get_rook_moves(board: int, rook_cell: int, masker: Masks) -> int:
    """ This method is using SBAMG algorithm to generate the rook's moves

    :param board: bitboard of the current gameboard
    :param rook_cell: the index of the rook's cell
    :param masker: a Masks object for diagonals' masks
    :return: a mask of the pseudo legal rook's moves
    """
    rank, file = translate_cell_to_row_col(rook_cell)

    mask = masker.get_rank_mask(rank)
    occ = (board & mask) | outer_cell(rook_cell)
    occ ^= (1 << rook_cell)
    bsq = bit_scan_reverse(occ & ((1 << rook_cell) - 1))
    cbn = 3 << bsq if rook_cell != 0 else 1
    occ = occ ^ (occ - cbn)
    result = occ & mask

    mask = masker.get_file_mask(file)
    occ = (board & mask) | outer_cell_file(rook_cell)
    occ ^= (1 << rook_cell)
    bsq = bit_scan_reverse(occ & ((1 << rook_cell) - 1))
    cbn = 3 << bsq
    occ = occ ^ (occ - cbn)
    result |= occ & mask

    return result


def get_queen_moves(board: int, queen_cell: int, masker: Masks) -> int:
    """ This method is using SBAMG algorithm to generate the queen's moves

    :param board: bitboard of the current gameboard
    :param queen_cell: the index of the queen's cell
    :param masker: a Masks object for diagonals' masks
    :return: a mask of the pseudo legal queen's moves
    """
    return get_rook_moves(board, queen_cell, masker) | get_bishop_moves(board, queen_cell, masker)
