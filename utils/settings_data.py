from dataclasses import dataclass
from .validation_utils import get_valid_int
from .constants import TRIANGLE_NUMBERS, BARRIER_DENSITY_TRANS


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
