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
