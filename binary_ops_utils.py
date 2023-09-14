def switch_bit(source: int, row: int, col: int, on: bool):
    if on:
        return source | (1 << (row * 8 + col))
    return source & (~(1 << (row * 8 + col)))


def switch_cell_bit(source: int, cell: int, on: bool):
    if on:
        return source | (1 << cell)
    return source & (~(1 << cell))


def translate_row_col_to_cell(row: int, col: int):
    if row > 8 or col > 8 or row < 1 or col < 1:
        return -1
    row = row - 1
    col = col - 1
    return row * 8 + col


def translate_cell_to_row_col(cell: int):
    return int(cell / 8), cell % 8


def get_turned_bits(word: int):
    result = []
    temp = word
    curr = 0
    while temp != 0:
        if temp & 1:
            result.append(curr)
        temp = temp >> 1
        curr += 1
    return result
