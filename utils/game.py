import random
from dataclasses import dataclass, field

from .board import Board
from .constants import POWERUPS, SCORES_PATH
from .other_utils import export_2d, import_2d, coord_to_string
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
        self.board.dot_coords[self.turn].sort(key=lambda x: (x[0], x[1]))

    def get_origin(self) -> tuple[int, int] | None:
        prompt = "Which dot would you like to move?"
        for i, coord in enumerate(self.board.dot_coords[self.turn], start=1):
            prompt += f"\n{i}) {coord_to_string(coord)}"
        exit_num = len(self.board.dot_coords[self.turn]) + 1
        prompt += f"\n{exit_num}) Cancel\n"
        selected = get_valid_int(prompt, 1, exit_num)
        if selected == exit_num:
            return None
        return self.board.dot_coords[self.turn][selected - 1]

    def detect_moves(self, origin: tuple[int, int], vectors: list[tuple[int, int]]) -> dict[str, tuple[int, int]]:
        moves = {key: self.calculate_move(origin, vector) for key, vector in zip("DASW", vectors)}
        return {direction: move for direction, move in moves.items() if move is not None}

    def get_destination(self, moves: dict[str, tuple[int, int]]) -> tuple[int, int] | None:
        prompt = "Which direction would you like to move?"
        DIRECTIONS = {"D": "Right", "A": "Left", "S": "Down", "W": "Up"}
        for direction in moves:
            prompt += f"\n{direction}) {DIRECTIONS[direction]}"
        prompt += "\nC) Cancel\n"
        accepted = ["C", "c"] + list(moves.keys()) + [key.lower() for key in moves.keys()]
        wasd = get_valid_str(prompt, 1, 1, accepted).upper()
        if wasd == "C":
            return None
        return moves[wasd]

    def actual_move(self, vectors: list[tuple[int, int]]) -> bool:
        while True:
            origin = self.get_origin()
            if origin is None:
                return False
            moves = self.detect_moves(origin, vectors)
            if not moves:
                print("This dot cannot move.")
                continue
            break
        destination = self.get_destination(moves)
        if destination is None:
            return False
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
                if self.edit_coord("Which space would you like to create?", " ", "/") is None:
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
