from pathlib import Path

from tabulate import tabulate


def import_2d(path: Path) -> list[list[str]]:
    with path.open("r") as file:
        return [line.strip().split(",") for line in file]


def export_2d(path: Path, array: list[list]) -> None:
    with path.open("w") as file:
        file.write("\n".join([",".join(line) for line in array]))


def show_scores(scores: list[list[str]]) -> None:
    print(tabulate(scores, headers=["Name", "Length", "Width", "Dots", "Turns"]))


def letters_to_index(letters: str) -> int:
    index = 0
    for letter in letters:
        index = index * 26 + (ord(letter.upper()) - ord("A") + 1)
    return index - 1


def coord_to_string(coord: tuple[int, int]) -> str:
    col_num = coord[0]
    col_parts = []
    while col_num >= 0:
        col_parts.append(chr(col_num % 26 + ord('A')))
        col_num = col_num // 26 - 1
    col_str = ''.join(reversed(col_parts))
    return f"{coord[1] + 1}{col_str}"


def string_to_coord(string: str) -> tuple[int, int]:
    row_str = ''.join(filter(str.isdigit, string))
    col_str = ''.join(filter(str.isalpha, string))
    row_num = int(row_str) - 1
    col_num = sum((ord(char.upper()) - ord('A') + 1) * (26 ** i)
                  for i, char in enumerate(reversed(col_str))) - 1
    return (col_num, row_num)
