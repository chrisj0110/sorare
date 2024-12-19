from dataclasses import dataclass
import enum


@dataclass(frozen=True)
class CustomScoring:
    points: float
    assists: float
    rebounds: float
    steals: float
    blocks: float
    threes_made: float
    turnovers: float
    double_double: float
    triple_double: float


class CustomScoringEnum(str, enum.Enum):
    normal = ("normal",)
    offense = ("offense",)
    defense = ("defense",)
    double_rebounds_assists = ("double_rebounds_assists",)


CUSTOM_SCORING_DICT: dict[str, CustomScoring] = {
    "normal": CustomScoring(points=1, assists=1.5, rebounds=1.2, threes_made=1, steals=3, blocks=3, turnovers=-2, double_double=1, triple_double=1),
    "offense": CustomScoring(points=1, assists=1.5, rebounds=1.2, threes_made=1, steals=0, blocks=0, turnovers=0, double_double=1, triple_double=1),
    "defense": CustomScoring(points=0, assists=0, rebounds=1.2, threes_made=0, steals=3, blocks=3, turnovers=0, double_double=0, triple_double=0),
    "double_rebounds_assists": CustomScoring(
        points=1, assists=3.0, rebounds=2.4, threes_made=1, steals=3, blocks=3, turnovers=-2, double_double=1, triple_double=1
    ),
}
