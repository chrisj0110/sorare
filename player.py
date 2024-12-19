from __future__ import annotations

import numpy as np
import warnings
from dataclasses import dataclass
from typing import cast


@dataclass(frozen=True)
class Player:
    url: str
    name: str
    ten_game_average: int
    ten_scores: list[int]
    game_count: int
    age: int
    dnp_count: int
    injury_status: str
    bonus: int
    simulation: int
    team: str

    @property
    def slope(self) -> float:
        scores_to_use = [score for score in self.ten_scores if score > 0]
        if not scores_to_use:
            return 0.0

        with warnings.catch_warnings():
            warnings.filterwarnings("error")
            try:
                slope, _ = np.polyfit(np.array(range(len(scores_to_use), 0, -1)), np.array(scores_to_use), 1)
                return cast(float, round(slope, 2))
            except np.RankWarning:
                return 0.0

    def to_csv(self) -> str:
        return ",".join(
            [
                self.name,
                str(self.ten_game_average),
                "",  # team
                str(self.simulation - self.ten_game_average),
                str(self.simulation),
                str(self.slope),
                str(self.game_count),
                str(self.bonus),
                str(self.age),
                str(self.dnp_count),
                self.injury_status,
                "_".join([str(x) for x in self.ten_scores]),
                f"{self.url} ",  # space to make the link clickable from the console
                self.team,
            ]
        )

    def render(self) -> str:
        # name, 10-game-avg, profit, game count, inj status, 10 scores, rotowire url
        return f"{self.ten_game_average:<3}{self.name:<26}{self.simulation - self.ten_game_average:<5}{self.game_count} games  {self.injury_status:<5}{'_'.join([str(s) for s in self.ten_scores]):<32}"

    @classmethod
    def from_csv_row(cls, csv_row: str) -> Player:
        (
            name,
            ten_game_average,
            empty_team,
            sim_minus_avg,
            simulation,
            slope,
            game_count,
            bonus,
            age,
            dnp_count,
            injury_status,
            ten_scores_str,
            url,
            team,
        ) = csv_row.split(",")

        if not ten_scores_str:
            ten_scores_str = "-100"

        return Player(
            url.strip(),
            name,
            int(ten_game_average),
            [int(x) for x in ten_scores_str.split("_")],
            int(game_count),
            int(age),
            int(dnp_count),
            injury_status,
            int(bonus),
            int(simulation),
            team,
        )
