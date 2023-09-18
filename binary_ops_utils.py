def switch_bit(source: int, row: int, col: int, on: bool):
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


def switch_cell_bit(source: int, cell: int, on: bool):
    """ Turn on or off 1 bit in the cell index.

    :param source: The original bit sequence
    :param cell: The cell index
    :param on: The boolean that says whether to turn the bit on or off
    :return: The modified int
    """

    if on:
        return source | (1 << cell)
    return source & (~(1 << cell))


def translate_row_col_to_cell(row: int, col: int):
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


def translate_cell_to_row_col(cell: int):
    """ This method convert given cell index to a row and a column.

    :param cell: The cell index
    :return: A tuple of the cell row and column
    """

    return int(cell / 8), cell % 8


def get_turned_bits(word: int):
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


def get_direction(cell: int, target: int):
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
