from mgr import roster_mgr
from player import Player


def test_get_players_from_team() -> None:
    players = [
        Player("dummy_sorare_url", "Marcus Smart", 30, [1, 2, 3, 4, 5], 2, 28, 0, "", 5, 3, "Boston Celtics"),
        Player("dummy_sorare_url", "Luka Doncic", 30, [1, 2, 3, 4, 5], 2, 28, 0, "", 5, 3, "Dallas Mavericks"),
        Player("dummy_sorare_url", "Jason Tatum", 30, [1, 2, 3, 4, 5], 2, 28, 0, "", 5, 3, "Boston Celtics"),
    ]
    assert len(roster_mgr.get_players_from_team(players, "Boston Celtics")) == 2


def test_get_players_sorted_by_score() -> None:
    players = [
        Player("dummy_sorare_url", "Marcus Smart", 30, [1, 2, 3, 4, 5], 2, 28, 0, "", 5, 3, "Boston Celtics"),
        Player("dummy_sorare_url", "Luka Doncic", 10, [1, 2, 3, 4, 5], 2, 28, 0, "", 5, 3, "Dallas Mavericks"),
        Player("dummy_sorare_url", "Jason Tatum", 20, [1, 2, 3, 4, 5], 2, 28, 0, "", 5, 3, "Boston Celtics"),
    ]
    results = roster_mgr.get_players_sorted_by_score(players)
    assert [player.ten_game_average for player in results] == [30, 20, 10]


def test_get_players_sorted_by_profit() -> None:
    players = [
        Player("dummy_sorare_url", "Marcus Smart", 30, [1, 2, 3, 4, 5], 2, 28, 0, "", 5, 30, "Boston Celtics"),
        Player("dummy_sorare_url", "Luka Doncic", 10, [1, 2, 3, 4, 5], 2, 28, 0, "", 5, 30, "Dallas Mavericks"),
        Player("dummy_sorare_url", "Jason Tatum", 20, [1, 2, 3, 4, 5], 2, 28, 0, "", 5, 30, "Boston Celtics"),
    ]
    results = roster_mgr.get_players_sorted_by_profit(players)
    assert [player.ten_game_average for player in results] == [10, 20, 30]
