from player import Player
from mgr import player_sim_mgr


def test_player_simulation() -> None:
    player = Player("dummy_sorare_url", "Marcus Smart", 30, [1, 2, 3, 4, 5], 2, 28, 0, "", 5, 3, "Boston Celtics")
    assert 1 <= player_sim_mgr.player_simulation(player, 2) <= 5
