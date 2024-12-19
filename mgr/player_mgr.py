import copy
from player import Player
from typing import Any


def update_player(player: Player, key: str, value: Any) -> Player:
    new_player = copy.deepcopy(player)
    player_data = new_player.__dict__
    player_data[key] = value
    return Player(**player_data)
