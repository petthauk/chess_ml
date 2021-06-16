letter_list = ["a", "b", "c", "d", "e", "f", "g", "h"]


def string_position_to_array_position(string_pos):
    try:
        for i in range(len(letter_list)):
            if string_pos != "":
                if string_pos[0] == letter_list[i]:
                    return [8-int(string_pos[1]), i]
    except ValueError:
        return None


def array_position_to_string_position(array_pos):
    string_pos = ""
    string_pos += letter_list[array_pos[1]]
    string_pos += str(8 - array_pos[0])
    return string_pos

