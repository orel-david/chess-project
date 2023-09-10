def switch_bit(source: int, row: int, col: int, on: bool):
    if on:
        return source | (1 << (row * 8 + col))
    return source & (~(1 << (row * 8 + col)))


def translate_row_col_to_cell(row: int, col: int):
    if row > 8 or col > 8 or row < 1 or col < 1:
        return -1
    return row * 8 + col


def translate_cell_to_row_col(cell: int):
    return cell / 8, cell % 8
