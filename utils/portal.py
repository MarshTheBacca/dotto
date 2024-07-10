from dataclasses import dataclass


@dataclass
class Portal:
    coord_1: tuple[int, int]
    coord_2: tuple[int, int]

    def is_member(self, coord: tuple[int, int]) -> bool:
        return coord == self.coord_1 or coord == self.coord_2

    def get_opposite(self, coord: tuple[int, int]) -> tuple[int, int]:
        return self.coord_1 if coord == self.coord_2 else self.coord_2
