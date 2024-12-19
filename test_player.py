from player import Player


def test_Player() -> None:
    player = Player(
        "https://sorare.com/nba/players/marcus-smart-19940306",
        "Marcus Smart",
        30,
        [1, 2, 3, 4, 5],
        2,
        28,
        0,
        "",
        5,
        3,
        "Boston Celtics",
    )
    assert "Marcus Smart,30,," in player.to_csv()
    assert "30 Marcus Smart" in player.render()

    new_player = Player.from_csv_row(player.to_csv())
    assert new_player.name == "Marcus Smart"
    assert new_player.ten_scores == [1, 2, 3, 4, 5]
