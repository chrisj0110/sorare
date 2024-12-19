from player import Player
from mgr import player_mgr


def test_update_player() -> None:
    player = Player("dummy_sorare_url", "Marcus Smart", 30, [1, 2, 3, 4, 5], 2, 28, 0, "", 5, 3, "Boston Celtics")
    updated_player = player_mgr.update_player(player, "age", 99)
    assert updated_player.age == 99
