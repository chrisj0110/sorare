import random
import statistics
from player import Player


def player_simulation(player: Player, game_count: int) -> int:
    if not game_count or sum(player.ten_scores) == 0:
        return 0

    RUNS = 10000
    non_zero_scores = [score for score in player.ten_scores if score > 0]
    if not non_zero_scores:
        return 0
    results: list[int] = [max([random.choice(non_zero_scores) for _ in range(game_count)]) for _ in range(RUNS)]

    return int(statistics.mean(results) * (1 + (player.bonus / 100)))
