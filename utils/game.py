import random
from dataclasses import dataclass, field

from .board import Board
from .constants import LETTERS, POWERUPS, SCORES_PATH
from .other_utils import export_2d, import_2d
from .portal import Portal
from .settings_data import SettingsData
from .validation_utils import (confirm, get_valid_coord, get_valid_int,
                               get_valid_str)

DOT_CHARS = {1: "O", 2: "X"}


@dataclass
class Game:
    settings: SettingsData
    inventory: dict[int, list[str]] = field(default_factory=lambda: {1: [], 2: []})

    def __post_init__(self) -> None:
        self.board = Board.from_settings(self.settings)
        self.deletes = {1: self.settings.num_deletes, 2: self.settings.num_deletes}
        self.creates = {1: self.settings.num_creates, 2: self.settings.num_creates}
        self.turn_number: int = 1
        self.turn = 1

    @property
    def target_char(self) -> str:
        return DOT_CHARS[3 - self.turn]

    @property
    def ally_char(self) -> str:
        return DOT_CHARS[self.turn]

    def edit_coord(self, prompt: str, target_char: str, new_char: str) -> tuple[int, int] | None:
        while True:
            coord = get_valid_coord(prompt, self.settings.length, self.settings.width)
            if coord is None:
                return None
            if self.board.get_char(coord) == target_char:
                self.board.replace_char(coord, new_char)
                return coord
            print(f"Coordinate does not correspond to {target_char}")

    def calculate_move(self, position: tuple[int, int], vector: tuple[int, int]) -> tuple[int, int] | None:
        destination = (position[0] + vector[0], position[1] + vector[1])
        if not self.board.is_within_bounds(destination):
            return None
        destination_char = self.board.get_char(destination)
        allowed_chars = ("/", self.target_char, "?", "~", "@", " ")
        if destination_char not in allowed_chars:
            return None
        elif destination_char == " ":
            return self.calculate_move(destination, vector)
        return destination

    def detect_moves(self, vectors: list[tuple[int, int]]) -> list[list[tuple[int, int] | None]]:
        return [[self.calculate_move(dot_coord, vector) for vector in vectors] for dot_coord in self.board.dot_coords[self.turn]]

    def update_portals(self, coord: tuple[int, int]) -> tuple[int, int]:
        for portal in self.board.portals:
            if portal.is_member(coord):
                self.board.replace_char(coord, "/")
                destination = portal.get_opposite(coord)
                self.board.portals.remove(portal)
                return destination
        raise ValueError("Coord is not a portal")

    def process_move(self, origin: tuple[int, int], destination: tuple[int, int]) -> None:
        if origin in self.board.crumblies:
            self.board.crumblies.remove(origin)
            self.board.replace_char(origin, " ")
        else:
            self.board.replace_char(origin, "/")
        destination_char = self.board.get_char(destination)
        if destination_char == "?":
            self.inventory[self.turn].append(random.choice(POWERUPS))
            print(f"Player {self.turn} picked up a {self.inventory[self.turn][-1]}!")
        elif destination_char == "@":
            destination = self.update_portals(destination)
        elif destination_char == "~":
            self.board.crumblies.append(destination)
        elif destination_char == self.target_char:  # capture their piece
            self.board.dot_coords[3 - self.turn].remove(destination)
        self.board.replace_char(destination, self.ally_char)
        self.board.dot_coords[self.turn].append(destination)
        self.board.dot_coords[self.turn].remove(origin)
        # sort coordinates by y, then x
        self.board.dot_coords[self.turn].sort(key=lambda x: (x[0], x[1]))

    def print_dot_options(self) -> str:
        line = "Which one would you like to move?"
        for index, (x, y) in enumerate(self.board.dot_coords[self.turn], start=1):
            line += f"\n{index}) {'0' if y + 1 < 10 and self.board.width > 9 else ''}{y + 1}{LETTERS[x]}"
        line += f"\n{len(self.board.dot_coords[self.turn]) + 1}) Cancel\n"
        return line

    def print_move_options(self, possible_moves: list[list[tuple[int, int] | None]], selected: int) -> tuple[str, list[str]]:
        DIRECTIONS = {"D": "Right", "A": "Left", "S": "Down", "W": "Up"}
        line = "Which direction would you like to move?"
        accepted = ["C", "c"]
        for i, move in enumerate(possible_moves[selected - 1]):
            if move is not None:
                key = "DASW"[i]
                line += f"\n{key}) {DIRECTIONS[key]}"
                accepted += [key, key.lower()]
        line += "\nC) Cancel\n"
        return line, accepted

    def actual_move(self, vectors: list[tuple[int, int]]) -> bool:
        possible_moves = self.detect_moves(vectors)
        print(possible_moves)
        line = self.print_dot_options()
        exit_num = len(self.board.dot_coords[self.turn]) + 1
        selected = get_valid_int(line, 1, exit_num)
        if selected == exit_num:
            return False

        if not any(possible_moves[selected - 1]):
            print("That dot can't move")
            return False

        line, accepted = self.print_move_options(possible_moves, selected)
        wasd = get_valid_str(line, 1, 1, accepted).upper()
        if wasd == "C":
            return False

        indexes = {"D": 0, "A": 1, "S": 2, "W": 3}
        origin = self.board.dot_coords[self.turn][selected - 1]
        destination = possible_moves[selected - 1][indexes[wasd]]
        self.process_move(origin, destination)
        return True

    def check_defeat(self) -> bool:
        for row in self.board.field:
            for char in row:
                if char == self.target_char:
                    return False
        return True

    def play(self) -> None:
        while True:
            if self.turn_number % self.settings.powerup_frequency == 0:
                self.board.place_powerup()
            self.board.show()
            print(f"Player {self.turn}'s Turn\t\t\tTurn: {self.turn_number}")
            option = get_valid_int("What would you like to do?\n1) Move\n2) Delete a space\n"
                                   "3) Create a space\n4) Use a powerup\n5) Concede\n", 1, 5)
            if option == 1:
                if not self.actual_move([[0, 1], [0, -1], [1, 0], [-1, 0]]):
                    continue
            elif option == 2:
                if self.deletes[self.turn] == 0:
                    print("You have run out of deletes")
                    continue
                print(f"Number of deletes remaining: {self.deletes[self.turn]}")
                if self.edit_coord("Which space would you like to delete?", "/", " ") is None:
                    continue
                self.deletes[self.turn] -= 1
            elif option == 3:
                if self.creates[self.turn] == 0:
                    print("You have run out of creates")
                    continue
                print(f"Number of creates remaining: {self.creates[self.turn]}")
                if self.edit_coord("Which space would you like to delete?", "/", " ") is None:
                    continue
                self.creates[self.turn] -= 1
            elif option == 4:
                if not self.inventory[self.turn]:
                    print("You don't have any powerups")
                    continue
                prompt = "Which one would you like to use?\n"
                for i, powerup in enumerate(self.inventory[self.turn]):
                    prompt += f"{i + 1}) {powerup}\n"
                exit_num = len(self.inventory[self.turn]) + 1
                prompt += f"{exit_num}) Cancel\n"
                choice = get_valid_int(prompt, 1, exit_num)
                if choice == exit_num:
                    continue
                chosen_powerup = self.inventory[self.turn][choice - 1]
                if chosen_powerup == "Portal":
                    coord_1 = self.edit_coord("Where would you like the entrance to your portal?", "/", "@")
                    if coord_1 is None:
                        continue
                    coord_2 = self.edit_coord("Where would you like the exit to your portal", "/", "@")
                    if coord_2 is None:
                        self.board.replace_char(coord_1, "/")  # undo the first portal
                        continue
                    self.board.portals.append(Portal(coord_1, coord_2))
                elif chosen_powerup == "Double-Jump" and not self.actual_move([[0, 2], [0, -2], [2, 0], [-2, 0]]):
                    continue
                elif chosen_powerup == "Destroyer" and self.edit_coord("Which barrier would you like to destroy?", "#", "/") is None:
                    continue
                del (self.inventory[self.turn][choice - 1])
            elif option == 5 and confirm("Are you sure?"):
                break
            if self.check_defeat():
                self.board.show()
                break
            self.turn = 1 if self.turn == 2 else 2
            self.turn_number += 1
        print(f"Player {self.turn} has won in {self.turn_number} turns!")
        if confirm("Would you like to save your scores?"):
            scores = import_2d(SCORES_PATH)
            scores.append([input("Enter your names"), self.board.length, self.board.width, self.settings.num_dots, self.turn_number])
            export_2d(SCORES_PATH, scores)
