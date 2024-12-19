from game_stats import GameStats


def test_game_stats() -> None:
    gs = GameStats(10, 8, 8, 2, 1, 0, 0)
    assert gs.double_double == 0
    assert gs.triple_double == 0

    gs = GameStats(10, 8, 12, 2, 1, 0, 0)
    assert gs.double_double == 1
    assert gs.triple_double == 0

    gs = GameStats(10, 8, 12, 12, 1, 0, 0)
    assert gs.double_double == 1
    assert gs.triple_double == 1
