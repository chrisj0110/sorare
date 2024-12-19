from pathlib import Path


IS_PLAYOFFS = False

# region custom playoff schedule
CUSTOM_TEAM_SCHEDULE = {  # for playoffs
    "Atlanta Hawks": 0,
    "Boston Celtics": 0,
    "Brooklyn Nets": 0,
    "Charlotte Hornets": 0,
    "Chicago Bulls": 0,
    "Cleveland Cavaliers": 0,
    "Dallas Mavericks": 0,
    "Denver Nuggets": 1,
    "Detroit Pistons": 0,
    "Golden State Warriors": 0,
    "Houston Rockets": 0,
    "Indiana Pacers": 0,
    "LA Clippers": 0,
    "Los Angeles Lakers": 0,
    "Memphis Grizzlies": 0,
    "Miami Heat": 1,
    "Milwaukee Bucks": 0,
    "Minnesota Timberwolves": 0,
    "New Orleans Pelicans": 0,
    "New York Knicks": 0,
    "Oklahoma City Thunder": 0,
    "Orlando Magic": 0,
    "Philadelphia 76ers": 0,
    "Phoenix Suns": 0,
    "Portland Trail Blazers": 0,
    "Sacramento Kings": 0,
    "San Antonio Spurs": 0,
    "Toronto Raptors": 0,
    "Utah Jazz": 0,
    "Washington Wizards": 0,
}
# endregion

# region misc
CSV_FOLDER = Path.cwd()
CSV_PATH = CSV_FOLDER / "predictions.csv"
CSV_PATH_BAK = CSV_FOLDER / "predictions_bak.csv"
CUSTOM_CSV_PATH = CSV_FOLDER / "predictions_custom.csv"
CUSTOM_CSV_PATH_BAK = CSV_FOLDER / "predictions_custom_bak.csv"
# endregion
