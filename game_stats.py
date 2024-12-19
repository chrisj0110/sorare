from dataclasses import dataclass


@dataclass(frozen=True)
class GameStats:
    points: int
    assists: int
    rebounds: int
    steals: int
    blocks: int
    threes_made: int
    turnovers: int

    @property
    def _double_digit_categories(self) -> int:
        return len(list(filter(lambda x: x >= 10, [self.points, self.assists, self.rebounds, self.steals, self.blocks])))

    @property
    def double_double(self) -> int:
        return 1 if self._double_digit_categories >= 2 else 0

    @property
    def triple_double(self) -> int:
        return 1 if self._double_digit_categories >= 3 else 0
