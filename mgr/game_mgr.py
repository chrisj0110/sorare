from custom_scoring import CustomScoring
from game_stats import GameStats


def get_game_score(custom_scoring: CustomScoring, game_stats: GameStats) -> int:
    score = custom_scoring.points * game_stats.points
    score += custom_scoring.assists * game_stats.assists
    score += custom_scoring.rebounds * game_stats.rebounds
    score += custom_scoring.steals * game_stats.steals
    score += custom_scoring.blocks * game_stats.blocks
    score += custom_scoring.threes_made * game_stats.threes_made
    score += custom_scoring.turnovers * game_stats.turnovers
    score += custom_scoring.double_double * game_stats.double_double
    score += custom_scoring.triple_double * game_stats.triple_double
    return int(score)
