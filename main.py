
import random
from pathlib import Path
from dataclasses import dataclass
from tabulate import tabulate

LETTERS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O"]
TRIANGLE_NUMBERS = [1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66, 78, 91, 105]
BARRIER_DENSITY_TRANS = {2: "Insanely Thick", 3: "Thick", 4: "Normal", 5: "Sparse"}
SCORES_PATH = Path(__file__).parent.joinpath("scores.txt")
TARGETS = [None, "X", "O"]
DOT_CHARS = [None, "O", "X"]


@dataclass
class SettingsData:
    length: int = 5
    width: int = 5
    num_dots: int = 3
    num_powerups: int = 2
    powerup_frequency: int = 5
    num_crumblies: int = 3
    barrier_density: int = 4
    num_deletes: int = 3
    num_creates: int = 3

    def edit(self) -> None:
        while True:
            option = get_valid_int("What would you like to do?\n1) Set Length\n2) Set Width\n3) Set Amount of Dots\n"
                                   "4) Set Amount of Start Powerups\n5) Set Frequency of Powerup Placement\n"
                                   "6) Change Number of Crumblies\n7) Set Barrier Density\n8) Set Number of Deletes\n9) Set Number of Creates\n10) Exit\n", 1, 10)
            if option == 1:
                self.length = get_valid_int("Enter your preffered length. (5-15)", 5, 15)
            elif option == 2:
                self.width = get_valid_int("Enter your preffered width. (5-15)", 5, 15)
            elif option == 3:
                self.num_dots = get_valid_int("Enter your preffered amount of dots. (Limited to your set dimentions)", 1, TRIANGLE_NUMBERS[self.length - 2] or TRIANGLE_NUMBERS[self.width - 2])
            elif option == 4:
                limit = self.length * self.width - self.num_dots * 2 - (self.length // 4) * (self.width // 4) * 4 - self.num_crumblies
                self.num_powerups = get_valid_int("Enter your preffered amount of start powerups (Limited to available spaces and number of crumblies: " + str(limit) + ")\n", 0, limit)
            elif option == 5:
                self.powerup_frequency = get_valid_int("Enter you preffered frequency of powerup placement\n", 1)
            elif option == 6:
                limit = self.length * self.width - self.num_dots * 2 - (self.length // 4) * (self.width // 4) * 4 - self.num_powerups
                self.num_crumblies = get_valid_int("Enter you preffered number of crumblies. (Limited to available spaces and number of powerups: " + str(limit) + ")\n", 0, limit)
            elif option == 7:
                conversions = {1: 4, 2: 3, 3: 5, 4: 2}
                self.barrier_density = conversions[get_valid_int("Enter your preffered density of barriers.\n1) Normal\n2) Medium\n3) Sparse\n4) Insanely Thick\n", 1, 4)]
            elif option == 8:
                self.num_deletes = get_valid_int("Enter your preffered number of deletes each player gets.", 0)
            elif option == 9:
                self.num_creates = get_valid_int("Enter your preffered number of creates each player gets.", 0)
            elif option == 10:
                break

    def __repr__(self) -> str:
        return (f"Settings:\n"
                f"Length: {self.length}\t"
                f"Width: {self.width}\n"
                f"Number of dots: {self.num_dots}\t"
                f"Number of powerups: {self.num_powerups}\n"
                f"Powerup frequency: {self.powerup_frequency}\t"
                f"Number of crumblies: {self.num_crumblies}\n"
                f"Barrier density: {BARRIER_DENSITY_TRANS[self.barrier_density]}\t"
                f"Number of deletes: {self.num_deletes}\n"
                f"Number of creates: {self.num_creates}\n")


def import_2d(path: Path) -> list[list[str]]:
    with path.open("r") as file:
        return [line.strip().split(",") for line in file]


def export_2d(path: Path, array: list[list]) -> None:
    with path.open("w") as file:
        file.write("\n".join([",".join(line) for line in array]))


def show_scores(scores) -> None:
    print(tabulate(scores, headers=["Name", "Length", "Width", "Dots", "Turns"]))


def get_valid_int(prompt: str, lower: float | int = float("-inf"),
                  upper: float | int = float("inf")) -> int:
    while True:
        try:
            ans = int(input(prompt))
        except ValueError:
            print("Answer is not an integer")
            continue
        if ans < lower or ans > upper:
            print("Answer is out of range")
            continue
        return ans


def confirm(prompt: str) -> bool:
    while True:
        ans = input(f"{prompt} (y or n)\n").lower()
        if ans == "y":
            return True
        elif ans == "n":
            return False
        print("Invalid answer")


def place_dots(field: list[list[str]], dot_char: str, dots_to_place: int) -> list[list[str]]:
    for i, num in enumerate(TRIANGLE_NUMBERS):
        if dots_to_place <= num:
            max_num_dots_in_row = i + 1
            break
    for row in field:
        for x in range(0, max_num_dots_in_row):
            if dots_to_place != 0:
                row[x] = dot_char
                dots_to_place -= 1
        max_num_dots_in_row -= 1
    return field


def print_field(field: list[list[str]], settings: SettingsData) -> None:
    print("\n")
    for i in range(0, len(field)):
        line = LETTERS[i] + "\t"
        for x in range(0, len(field[i])):
            line += field[i][x] + "\t"
        print(line)
    line = "\t"
    for i in range(1, settings.width + 1):
        if settings.width > 9 and i < 10:
            line += "0"
        line += str(i) + "\t"
    print("\n" + line)


def get_valid_str(string, lower, upper, accepted: list[str] | None = None, exception: str | None = None) -> str | None:
    while True:
        ans = input(string)
        if exception is not None and ans == exception:
            return None
        if len(ans) < lower or len(ans) > upper:
            print("That answer is invalid")
            continue
        if accepted is not None:
            all_chars_accepted = True
            for char in ans:
                if char not in accepted:
                    print(f"Answer must not contain {char}")
                    all_chars_accepted = False
                    break
            if all_chars_accepted:
                return ans


def letters_to_index(letters: str) -> int:
    index = 0
    for letter in letters:
        index = index * 26 + (ord(letter.upper()) - ord("A") + 1)
    return index - 1


def get_valid_coord(prompt: str, length: int, width: int, exit_string: str = "c") -> tuple[int, int] | None:
    num_digits = len(str(width))
    if length <= 26:
        num_letters = 1
    elif length <= 26**2:
        num_letters = 2
    else:
        num_letters = 3

    while True:
        coord = input(f"{prompt}. Enter coordinate (e.g., 1A or 001AAA for larger boards, '{exit_string}' to cancel)\n")
        if coord == exit_string:
            return None
        if len(coord) < num_digits + num_letters:
            print(f"Coordinate is not the correct number of characters ({num_digits + num_letters})")
            continue
        numeric_part, alphabetic_part = coord[:num_digits], coord[num_digits:]
        if not numeric_part.isdigit() or not alphabetic_part.isalpha():
            print("Coordinate is not valid")
            continue
        x = int(numeric_part) - 1
        y = letters_to_index(alphabetic_part)
        if x < 0 or x >= width or y < 0 or y >= length:
            print("Coordinate is out of bounds")
            continue
        return y, x


def editing(field: list[list[str]], settings: SettingsData, prompt: str,
            target_char: str, new_char: str) -> tuple[int, int] | None:
    while True:
        coord = get_valid_coord(prompt, settings.length, settings.width)
        if coord is None:
            return None
        if field[coord[0]][coord[1]] == target_char:
            field[coord[0]][coord[1]] = new_char
            return coord
        print(f"Coordinate does not correspond to {target_char}")


def is_within_bounds(x: int, y: int, length: int, width: int) -> bool:
    return 0 <= x < length and 0 <= y < width


def find_portal_destination(portal_pos: tuple[int, int], portals: list[tuple[tuple[int, int], tuple[int, int]]]) -> tuple[int, int] | None:
    for portal_pair in portals:
        if portal_pos in portal_pair:
            return portal_pair[1] if portal_pos == portal_pair[0] else portal_pair[0]
    return None


def calculate_move(position: tuple[int, int], vector: tuple[int, int],
                   field: list[list[str]], allowed: tuple[str],
                   length: int, width: int, portals: list[tuple[tuple[int, int], tuple[int, int]]]) -> tuple[int, int] | None:
    new_pos = (position[0] + vector[0], position[1] + vector[1])
    print(new_pos)
    if not is_within_bounds(new_pos[0], new_pos[1], length, width):
        return None
    cell_value = field[new_pos[0]][new_pos[1]]
    if cell_value not in allowed:
        return None
    elif cell_value == " ":
        return calculate_move(new_pos, vector, field, allowed, length, width, portals)
    return new_pos


def detect_moves(field: list[list[str]], dot_coords: list[tuple[int, int]],
                 vectors: list[tuple[int, int]], target: str,
                 portals: list[tuple[tuple[int, int], tuple[int, int]]]) -> list[list[tuple[int, int] | None]]:
    allowed_chars = ("/", target, "?", "~", "@", " ")
    length, width = len(field), len(field[0])
    return [[calculate_move(dot_coord, vector, field, allowed_chars, length, width, portals)
             for vector in vectors] for dot_coord in dot_coords]


def print_dot_options(dot_coords: list[tuple[int, int]], settings: SettingsData):
    line = "Which one would you like to move?"
    for index, (x, y) in enumerate(dot_coords, start=1):
        line += f"\n{index}) {'0' if y + 1 < 10 and settings.width > 9 else ''}{y + 1}{LETTERS[x]}"
    line += f"\n{len(dot_coords) + 1}) Cancel\n"
    return line


def print_move_options(possible_moves: list[list[tuple[int, int] | None]], selected: int) -> tuple[str, list[str]]:
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


def process_move(field: list[list[str]], origin: tuple[int, int], destination: tuple[int, int],
                 crumblies: list[tuple[int, int]], inventory, turn: int, powerups: list[tuple[int, int]],
                 portals: list[tuple[tuple[int, int], tuple[int, int]]]) -> None:
    if origin in crumblies:
        crumblies.remove(origin)
        field[origin[0]][origin[1]] = " "
    else:
        field[origin[0]][origin[1]] = "/"
    destination_char = field[destination[0]][destination[1]]
    if destination_char == "?":
        inventory[turn].append(random.choice(powerups))
        print(f"Player {turn} picked up a {inventory[turn][-1]}!")
    elif destination_char == "@":
        destination = update_portals(field, destination, portals)
    elif destination_char == "~":
        crumblies.append(destination)
    field[destination[0]][destination[1]] = DOT_CHARS[turn]


def update_portals(field: list[list[str]], position: tuple[int, int],
                   portals: list[tuple[tuple[int, int], tuple[int, int]]]) -> tuple[int, int]:
    for portal_pair in portals:
        if position in portal_pair:
            field[position[0]][position[1]] = "/"
            destination = portal_pair[1] if position == portal_pair[0] else portal_pair[0]
            portals.remove(portal_pair)
            return destination
    raise ValueError("Position is not a portal")


def actual_move(field: list[list[str]], settings: SettingsData,
                vectors, turn, inventory, crumblies, portals, target) -> bool:
    powerups = ["Portal", "Double-Jump", "Destroyer"]
    dot_char = DOT_CHARS[turn]
    dot_coords = [(x, y) for x in range(len(field)) for y in range(len(field[0])) if field[x][y] == dot_char]
    possible_moves = detect_moves(field, dot_coords, vectors, target, portals)
    print(possible_moves)
    line = print_dot_options(dot_coords, settings)
    exit_num = len(dot_coords) + 1
    selected = get_valid_int(line, 1, exit_num)
    if selected == exit_num:
        return False

    if not any(possible_moves[selected - 1]):
        print("That dot can't move")
        return False

    line, accepted = print_move_options(possible_moves, selected)
    wasd = get_valid_str(line, 1, 1, accepted).upper()
    if wasd == "C":
        return False

    indexes = {"D": 0, "A": 1, "S": 2, "W": 3}
    origin = dot_coords[selected - 1]
    destination = possible_moves[selected - 1][indexes[wasd]]
    process_move(field, origin, destination, crumblies, inventory, turn, powerups, portals)
    return True


def replace_char(field: list[list[str]], powerups_to_place: int, new_char: str) -> list[list[str]]:
    MAX_ITERATIONS = 100
    num_iterations = 0
    length = len(field)
    width = len(field[0])
    while powerups_to_place > 0 and num_iterations < MAX_ITERATIONS:
        rand_index_1 = random.randint(0, length - 1)
        rand_index_2 = random.randint(0, width - 1)
        if field[rand_index_1][rand_index_2] == "/":
            field[rand_index_1][rand_index_2] = new_char
            powerups_to_place -= 1
        num_iterations += 1
    return field


def can_place_barrier(field: list[list[str]], base_coord: tuple[int, int], barrier_shape: list[list[int]]) -> bool:
    for dx, dy in barrier_shape:
        x, y = base_coord[0] + dx, base_coord[1] + dy
        if not (0 <= x < len(field) and 0 <= y < len(field[0])) or field[x][y] != "/":
            return False
    return True


def place_barriers(field: list[list[str]], settings: SettingsData) -> list[list[str]]:
    #   #       #     #     #
    #   # # #   # #   #   # #
    #           #     #
    barrier_coords = [[[0, 0], [1, 0], [0, 1], [0, 2]],
                      [[0, 0], [1, 0], [0, 1], [-1, 0]],
                      [[0, 0], [1, 0], [-1, 0]],
                      [[0, 0], [0, -1], [1, 0]]]
    barriers_to_place = (settings.length // settings.barrier_density) * (settings.width // settings.barrier_density)
    MAX_ITERATIONS = 1000
    num_iterations = 0
    while barriers_to_place > 0 and num_iterations < MAX_ITERATIONS:
        rand_coord = (random.randint(0, settings.length - 1), random.randint(0, settings.width - 1))
        rand_barrier = random.choice(barrier_coords)
        if can_place_barrier(field, rand_coord, rand_barrier):
            for dx, dy in rand_barrier:
                field[rand_coord[0] + dx][rand_coord[1] + dy] = "#"
            barriers_to_place -= 1
        num_iterations += 1
    return field


def generate_field(settings: SettingsData) -> list[list[str]]:
    field = [["/" for _ in range(settings.width)] for _ in range(settings.length)]
    field = place_dots(field, "X", settings.num_dots)
    field = [row[::-1] for row in field][::-1]
    field = place_dots(field, "O", settings.num_dots)
    field = replace_char(field, settings.num_powerups, "?")
    field = place_barriers(field, settings)
    field = replace_char(field, settings.num_crumblies, "~")
    return field


def check_finished(field: list[list[str]], target_char: str) -> bool:
    for row in field:
        for char in row:
            if char == target_char:
                return False
    return True


def play(settings: SettingsData) -> None:
    print(settings)
    inventory = [None, [], []]
    portals = []
    crumblies = []
    field = generate_field(settings)
    turn = 1
    turn_number = 1
    deletes_creates = [[], [settings.num_deletes, settings.num_creates], [settings.num_deletes, settings.num_creates]]
    while True:
        if turn_number % settings.powerup_frequency == 0:
            field = replace_char(field, 1, "?")
        target = TARGETS[turn]
        print_field(field, settings)
        print(f"Player {turn}'s Turn\t\t\tTurn: {turn_number}")
        option = get_valid_int("What would you like to do?\n1) Move\n2) Delete a space\n"
                               "3) Create a space\n4) Use a powerup\n5) Concede\n", 1, 5)
        if option == 1:
            if not actual_move(field, settings, [[0, 1], [0, -1], [1, 0], [-1, 0]], turn, inventory, crumblies, portals, target):
                continue
        elif option == 2:
            if deletes_creates[turn][0] == 0:
                print("You have run out of deletes")
                continue
            print(f"Number of deletes remaining: {deletes_creates[turn][0]}")
            if editing(field, settings, "Which space would you like to delete?", "/", " ") is None:
                continue
            deletes_creates[turn][0] -= 1
        elif option == 3:
            if deletes_creates[turn][1] == 0:
                print("You have run out of creates")
                continue
            print("Number of creates remaining:\t" + str(deletes_creates[turn][1]))
            if editing(field, settings, "Which space would you like to create", " ", "/") is None:
                continue
            deletes_creates[turn][1] -= 1
        elif option == 4:
            if len(inventory[turn]) == 0:
                print("You don't have any powerups")
                continue
            prompt = "Which one would you like to use?\n"
            for i, powerup in enumerate(inventory[turn]):
                prompt += f"{i + 1}) {powerup}\n"
            exit_num = len(inventory[turn]) + 1
            prompt += f"{exit_num}) Cancel\n"
            choice = get_valid_int(prompt, 1, exit_num)
            if choice == exit_num:
                continue
            chosen_powerup = inventory[turn][choice - 1]
            if chosen_powerup == "Portal":
                coord_1 = editing(field, settings, "Where would you like the entrance to your portal?", "/", "@")
                if coord_1 is None:
                    continue
                coord_2 = editing(field, settings, "Where would you like the exit to your portal", "/", "@")
                if coord_2 is None:
                    field[coord_1[0]][coord_1[1]] = "/"  # Undo the first portal
                    continue
                portals.append([coord_1, coord_2])
            elif chosen_powerup == "Double-Jump" and not actual_move(field, settings, [[0, 2], [0, -2], [2, 0], [-2, 0]], turn, inventory, crumblies, portals, target):
                continue
            elif chosen_powerup == "Destroyer" and editing(field, settings, "Which barrier would you like to destroy?", "#", "/") is None:
                continue
            del (inventory[turn][choice - 1])
        elif option == 5 and confirm("Are you sure?"):
            break
        if check_finished(field, target):
            print_field(field, settings)
            break
        turn = 1 if turn == 2 else 2
        turn_number += 1
    print("Player", str(turn), "has won in", turn_number, "turns!")
    if confirm("Would you like to save your scores?"):
        scores = import_2d(SCORES_PATH)
        scores.append([input("Enter your names"), str(settings.length), str(settings.width), str(settings.num_dots), str(turn_number)])
        export_2d(SCORES_PATH, scores)


def main() -> None:
    settings = SettingsData()
    while True:
        print("===========================\n     Welcome To Dotto!     \n===========================")
        option = get_valid_int("What would you like to do?\n1) Play\n2) Settings\n3) View Scores\n4) Exit\n", 1, 4)
        if option == 1:
            play(settings)
        elif option == 2:
            settings.edit()
        elif option == 3:
            show_scores(import_2d(SCORES_PATH))
        elif option == 4:
            break


if __name__ == "__main__":
    main()
