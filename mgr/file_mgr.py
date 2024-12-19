from pathlib import Path
from player import Player
from constants import CSV_PATH


def save_to_csv(players: list[Player], file_path: Path = CSV_PATH) -> None:
    file_path.write_text("\n".join(player.to_csv() for player in players), encoding="utf-8")


def load_from_csv(file_path: Path = CSV_PATH) -> list[Player]:
    lines: list[str] = file_path.read_text(encoding="utf-8").split("\n")
    return [Player.from_csv_row(line) for line in lines]
