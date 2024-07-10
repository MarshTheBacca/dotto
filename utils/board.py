from __future__ import annotations

import random
from dataclasses import dataclass

from .constants import LETTERS, TRIANGLE_NUMBERS
from .portal import Portal
from .settings_data import SettingsData


def place_dots(field: list[list[str]], dot_char: str,
               dots_to_place: int) -> list[list[str]]:
    for i, num in enumerate(TRIANGLE_NUMBERS):
        if dots_to_place <= num:
            max_num_dots_in_row = i + 1
            break
    for x, row in enumerate(field):
        for y in range(0, max_num_dots_in_row):
            if dots_to_place != 0:
                row[y] = dot_char
                dots_to_place -= 1
        max_num_dots_in_row -= 1
    return field


def random_replace(field: list[list[str]], num_to_replace: int,
                   new_char: str) -> tuple[list[list[str]], list[tuple[int, int]]]:
    MAX_ITERATIONS = 100
    num_iterations = 0
    length = len(field)
    width = len(field[0])
    replaced_coords = []
    while num_to_replace > 0 and num_iterations < MAX_ITERATIONS:
        rand_index_1 = random.randint(0, length - 1)
        rand_index_2 = random.randint(0, width - 1)
        if field[rand_index_1][rand_index_2] == "/":
            field[rand_index_1][rand_index_2] = new_char
            replaced_coords.append((rand_index_1, rand_index_2))
            num_to_replace -= 1
        num_iterations += 1
    return field, replaced_coords


def can_place_barrier(field: list[list[str]], base_coord: tuple[int, int],
                      barrier_shape: list[list[int]]) -> bool:
    for dx, dy in barrier_shape:
        x, y = base_coord[0] + dx, base_coord[1] + dy
        if not (0 <= x < len(field) and 0 <= y < len(field[0])) or field[x][y] != "/":
            return False
    return True


def place_barriers(field: list[list[str]],
                   settings: SettingsData) -> tuple[list[list[str]], list[tuple[int, int]]]:
    #   #       #     #     #
    #   # # #   # #   #   # #
    #           #     #
    barrier_layouts = [[[0, 0], [1, 0], [0, 1], [0, 2]],
                       [[0, 0], [1, 0], [0, 1], [-1, 0]],
                       [[0, 0], [1, 0], [-1, 0]],
                       [[0, 0], [0, -1], [1, 0]]]
    barriers_to_place = (settings.length // settings.barrier_density) * (settings.width // settings.barrier_density)
    MAX_ITERATIONS = 1000
    num_iterations = 0
    barrier_coords = []
    while barriers_to_place > 0 and num_iterations < MAX_ITERATIONS:
        rand_coord = (random.randint(0, settings.length - 1), random.randint(0, settings.width - 1))
        rand_barrier = random.choice(barrier_layouts)
        if can_place_barrier(field, rand_coord, rand_barrier):
            for dx, dy in rand_barrier:
                field[rand_coord[0] + dx][rand_coord[1] + dy] = "#"
                barrier_coords.append((rand_coord[0] + dx, rand_coord[1] + dy))
            barriers_to_place -= 1
        num_iterations += 1
    return field, barrier_coords


@dataclass
class Board:
    field: list[list[str]]
    crumblies: list[tuple[int, int]]
    powerups: list[tuple[int, int]]
    barriers: list[tuple[int, int]]
    portals: list[tuple[Portal, Portal]]

    def __post_init__(self) -> None:
        self.length = len(self.field)
        self.width = len(self.field[0])
        self.dot_coords = {1: self.scan_char_coords("O"), 2: self.scan_char_coords("X")}

    def scan_char_coords(self, target_char: str) -> list[tuple[int, int]]:
        return [(x, y) for x, row in enumerate(self.field)
                for y, char in enumerate(row) if char == target_char]

    @staticmethod
    def from_settings(settings: SettingsData) -> Board:
        field = [["/" for _ in range(settings.width)] for _ in range(settings.length)]
        field = place_dots(field, "X", settings.num_dots)
        field = [row[::-1] for row in field][::-1]
        field = place_dots(field, "O", settings.num_dots)
        field, powerup_coords = random_replace(field, settings.num_powerups, "?")
        field, barrier_coords = place_barriers(field, settings)
        field, crumblies_coords = random_replace(field, settings.num_crumblies, "~")
        return Board(field, crumblies_coords, powerup_coords, barrier_coords, [])

    def place_powerup(self) -> None:
        self.field, powerup_coords = random_replace(self.field, 1, "?")
        self.powerups.append(powerup_coords[0])

    def get_char(self, coord: tuple[int, int]) -> str:
        return self.field[coord[0]][coord[1]]

    def replace_char(self, coord: tuple[int, int], new_char: str) -> None:
        self.field[coord[0]][coord[1]] = new_char

    def is_within_bounds(self, coord: tuple[int, int]) -> bool:
        return 0 <= coord[0] < self.length and 0 <= coord[1] < self.width

    def show(self) -> None:
        print("\n")
        for i, row in enumerate(self.field):
            print(f"{LETTERS[i]}\t{'\t'.join(row)}")
        line = "\t"
        for i in range(1, self.width + 1):
            if self.width > 9 and i < 10:
                line += "0"
            line += str(i) + "\t"
        print("\n" + line)
