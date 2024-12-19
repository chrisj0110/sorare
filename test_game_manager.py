from custom_scoring import CustomScoring
from mgr import game_mgr
from game_stats import GameStats


def test_get_game_score() -> None:
    assert game_mgr.get_game_score(CustomScoring(1, 2, 3, 4, 5, 6, 7, 1, 1), GameStats(1, 2, 3, 4, 5, 6, 7)) == 140
