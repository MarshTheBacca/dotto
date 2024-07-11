import re

from .other_utils import letters_to_index, string_to_coord


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


def get_valid_str(string, lower, upper, accepted: list[str] | None = None,
                  cancel_string: str | None = None) -> str | None:
    while True:
        ans = input(string)
        if cancel_string is not None and ans == cancel_string:
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


def get_valid_coord(prompt: str, length: int, width: int, exit_string: str = "c") -> tuple[int, int] | None:
    while True:
        coord = input(f"{prompt}. Enter coordinate (e.g. 1A, '{exit_string}' to cancel)\n")
        if coord == exit_string:
            return None
        if not re.match(r"^\d+[A-Z]+$", coord):
            print("Invalid coordinate format")
            continue
        coord = string_to_coord(coord)
        if coord[0] < 0 or coord[0] >= width or coord[1] < 0 or coord[1] >= length:
            print("Coordinate is out of bounds")
            continue
        return coord
