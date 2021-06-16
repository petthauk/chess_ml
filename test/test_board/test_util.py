from board import util

letter_pos = ["a", "b", "c", "d", "e", "f", "g", "h"]
number_pos = [str(i) for i in range(8, 0, -1)]
all_string_pos = []
for number in number_pos:
    for letter in letter_pos:
        all_string_pos.append(letter + number)


def test_string_position_to_array_position():
    array_row = 0
    array_col = 0
    for pos in all_string_pos:
        assert util.string_position_to_array_position(pos) == [array_row, array_col]
        array_col += 1
        if array_col == 8:
            array_col = 0
            array_row += 1


def test_array_position_to_string_position():
    array_row = 0
    array_col = 0
    for pos in all_string_pos:
        assert util.array_position_to_string_position([array_row, array_col]) == pos
        array_col += 1
        if array_col == 8:
            array_col = 0
            array_row += 1
