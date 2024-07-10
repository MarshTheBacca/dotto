from pathlib import Path

LETTERS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O"]
TRIANGLE_NUMBERS = [1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66, 78, 91, 105]
BARRIER_DENSITY_TRANS = {2: "Insanely Thick", 3: "Thick", 4: "Normal", 5: "Sparse"}
SCORES_PATH = Path(__file__).parents[1].joinpath("scores.csv")
POWERUPS = ("Portal", "Double-Jump", "Destroyer")
