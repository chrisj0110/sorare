from player import Player


def get_players_from_team(players: list[Player], team: str) -> list[Player]:
    return [p for p in players if team.lower() in p.team.lower()]


def get_players_sorted_by_score(players: list[Player]) -> list[Player]:
    return list(reversed(sorted(players, key=lambda x: x.ten_game_average)))


def get_players_sorted_by_profit(players: list[Player]) -> list[Player]:
    return list(reversed(sorted(players, key=lambda x: x.simulation - x.ten_game_average)))


def output_to_console(players: list[Player]) -> None:
    for player in players:
        print(player.render())
