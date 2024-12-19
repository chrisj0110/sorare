from __future__ import annotations

import itertools
import os
import shutil
from functools import cache

import bcrypt
import requests
import typer
from bs4 import BeautifulSoup

from constants import IS_PLAYOFFS, CUSTOM_TEAM_SCHEDULE, CSV_PATH, CSV_PATH_BAK, CUSTOM_CSV_PATH, CUSTOM_CSV_PATH_BAK
from custom_scoring import CustomScoring, CustomScoringEnum, CUSTOM_SCORING_DICT
from mgr import file_mgr, game_mgr, player_mgr, player_sim_mgr, roster_mgr
from game_stats import GameStats
from player import Player

app = typer.Typer(pretty_exceptions_show_locals=False)


# __ actions __


# region EspnActionManager
class EspnActionManager:
    @staticmethod
    @cache
    def _get_injury_dict() -> dict[str, str]:
        """get injury dict of player name => injury status"""
        response = requests.get("https://www.espn.com/nba/injuries")
        soup = BeautifulSoup(response.content, "html.parser")

        injury_dict = {}

        tables = soup.find_all("table")
        for table in tables:
            tbody = table.find("tbody")
            for row in tbody.find_all("tr"):
                player_name = row.find_all("td")[0].text
                injury_status = row.find_all("td")[3].text
                injury_dict[player_name] = injury_status

        return injury_dict

    @staticmethod
    def get_injury_status_for_player_name(full_name: str) -> str:
        result = EspnActionManager._get_injury_dict().get(full_name, "")
        result = result.replace("Day-To-Day", "DTD")
        return result


# endregion


# region SorareApiManager
class SorareApiManager:
    """Sorare api

    https://api.sorare.com/sports/graphql/playground

    https://github.com/sorare/api"""

    @staticmethod
    @cache
    def _get_token() -> str:
        """get token once per session (it lasts like a year)"""
        email = os.getenv("sorare_email")
        assert email is not None

        password = os.getenv("sorare_password")
        assert password is not None

        salt = os.getenv("sorare_salt")
        assert salt is not None

        query = """
mutation SignInMutation($input: signInInput!) {
signIn(input: $input) {
    currentUser {
    slug
    jwtToken(aud: "personal") {
        token
        expiredAt
    }
    }
    otpSessionChallenge
    errors {
    message
    }
}
}
        """

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt.encode("utf-8"))

        variables = {"input": {"email": email, "password": hashed_password.decode()}}

        response = requests.post("https://api.sorare.com/graphql", json={"query": query, "variables": variables})

        otp_session_challenge = response.json()["data"]["signIn"]["otpSessionChallenge"]

        code_2fa = input("Enter 2fa code: ")
        assert code_2fa, "Missing 2fa code"

        query_2fa = 'mutation SignInMutation($input: signInInput!) { signIn(input: $input) { currentUser { slug jwtToken(aud: "personal") { token expiredAt } } errors { message } } }'
        variables_2fa = {"input": {"otpSessionChallenge": otp_session_challenge, "otpAttempt": code_2fa}}

        response = requests.post("https://api.sorare.com/graphql", json={"query": query_2fa, "variables": variables_2fa})

        # The response should contain a JSON object with an access token
        token = response.json()["data"]["signIn"]["currentUser"]["jwtToken"]["token"]
        assert token, "Could not get sorare api token"

        return str(token)

    @staticmethod
    @cache
    def get_open_game_week() -> int:
        query = """
query {
  nbaOpenFixture {
    id
    gameWeek
    fixtureState
  }
}
    """
        response = requests.post(
            "https://api.sorare.com/sports/graphql",
            headers={"content-type": "application/json", "Authorization": f"Bearer {SorareApiManager._get_token()}", "JWT-AUD": "personal"},
            json={"query": query},
        )
        api_response: dict = response.json()
        return int(api_response["data"]["nbaOpenFixture"]["gameWeek"])

    @staticmethod
    def get_all_my_players(game_week: int, custom_scoring: CustomScoring) -> tuple[list[Player], list[Player]]:
        """get all players (tuple of normal players, and custom players), one for each card I own"""
        query = """
{
  currentSportsUser() {
    nbaCards(first: 1000) {
      nodes {
        id
        slug
        player {
          id
          slug
          displayName
          age
          tenGameAverage
          team {
            fullName
          }
          latestFixtureStats(last: 14) {
            score
            fixture {
              fixtureState
              startDate
              endDate
            }
            status {
              statusIconType
              gameStats {
                score
                game {
                  startDate
                  homeTeam {
                      fullName
                  }
                  awayTeam {
                      fullName
                  }
                }
                detailedStats {
                  points
                  rebounds
                  assists
                  blocks
                  steals
                  turnovers
                  made3PointFGs
                  doubleDoubles
                  tripleDoubles
                  secondsPlayed
                }
              }
            }
          }
          upcomingGames(next: 4) {
            status
            homeTeam {
              fullName
            }
            awayTeam {
              fullName
            }
            startDate
            gameWeek
          }
          isActive
        }
        rarity
        totalBonus
      }
      pageInfo {
        endCursor
        hasNextPage
      }
    }
  }
}
    """
        response = requests.post(
            "https://api.sorare.com/sports/graphql",
            headers={"content-type": "application/json", "Authorization": f"Bearer {SorareApiManager._get_token()}", "JWT-AUD": "personal"},
            json={"query": query},
        )
        api_response: dict = response.json()

        players: list[Player] = []
        custom_players: list[Player] = []
        node: dict
        for node in api_response["data"]["currentSportsUser"]["nbaCards"]["nodes"]:
            player = node["player"]

            name = player["displayName"]

            ten_scores = SorareApiManager._get_ten_game_scores(player)

            bonus = int(node["totalBonus"] * 100)
            if node["rarity"] == "limited":
                bonus += 40

            player_team: str = player["team"]["fullName"] if player["team"] else "None"

            new_player = Player(
                url=f"https://sorare.com/nba/players/{player['slug']}/description",
                name=name,
                ten_game_average=player["tenGameAverage"],
                ten_scores=ten_scores,
                game_count=CUSTOM_TEAM_SCHEDULE.get(player_team, 0) if IS_PLAYOFFS else SorareApiManager._get_game_count(player, game_week),
                age=player["age"],
                dnp_count=len(list(itertools.takewhile(lambda x: x == 0, ten_scores))),
                injury_status=EspnActionManager.get_injury_status_for_player_name(name),
                bonus=bonus,
                simulation=0,  # we'll update this on the next line
                team=player_team,
            )
            players.append(player_mgr.update_player(new_player, "simulation", player_sim_mgr.player_simulation(new_player, new_player.game_count)))

            custom_player = player_mgr.update_player(new_player, "ten_scores", SorareApiManager._get_ten_game_custom_scores(player, custom_scoring))
            custom_players.append(
                player_mgr.update_player(custom_player, "simulation", player_sim_mgr.player_simulation(custom_player, custom_player.game_count))
            )

        return (players, custom_players)

    @staticmethod
    def _get_all_game_stats(player: dict) -> list[dict]:
        results: list[dict] = []
        for latest_fixture_stat in player["latestFixtureStats"]:
            if latest_fixture_stat["fixture"]["fixtureState"] == "opened":
                continue

            for game_stat in latest_fixture_stat["status"].get("gameStats", []):
                results.append(game_stat)
        return results

    @staticmethod
    def _get_ten_game_scores(player: dict) -> list[int]:
        """get last ten game scores given the player dict from their json response"""
        all_game_stats = SorareApiManager._get_all_game_stats(player)
        return [int(game_stats["score"]) for game_stats in all_game_stats[:10]]

    @staticmethod
    def _get_game_count(player: dict, game_week: int) -> int:
        """get game count givent he player dict from their json response"""
        game_week_games: list[dict] = [game for game in player["upcomingGames"] if game["gameWeek"] == game_week]
        return len(game_week_games)

    @staticmethod
    def _get_ten_game_custom_scores(player: dict, custom_scoring: CustomScoring) -> list[int]:
        """get last ten custom scores given a player dict from their json response"""
        zipped_values: list[tuple[int, ...]] = []
        all_game_stats: list[dict] = SorareApiManager._get_all_game_stats(player)
        for game_stats in all_game_stats:
            if game_stats["score"] == 0:
                zipped_values.append((0, 0, 0, 0, 0, 0, 0))
            else:
                zipped_values.append(
                    (
                        game_stats["detailedStats"]["points"],
                        game_stats["detailedStats"]["assists"],
                        game_stats["detailedStats"]["rebounds"],
                        game_stats["detailedStats"]["steals"],
                        game_stats["detailedStats"]["blocks"],
                        game_stats["detailedStats"]["made3PointFGs"],
                        game_stats["detailedStats"]["turnovers"],
                    )
                )
        return [game_mgr.get_game_score(custom_scoring, GameStats(*game_tuple)) for game_tuple in zipped_values[:10]]


def test_get_ten_game_scores() -> None:
    player = {
        "latestFixtureStats": [
            {
                "fixture": {
                    "fixtureState": "opened",
                },
                "status": {"gameStats": []},
            },
            {
                "fixture": {
                    "fixtureState": "started",
                },
                "status": {
                    "gameStats": [
                        {
                            "score": 11.5,
                        }
                    ]
                },
            },
            {
                "fixture": {
                    "fixtureState": "closed",
                },
                "status": {"gameStats": []},
            },
            {
                "fixture": {
                    "fixtureState": "closed",
                },
                "status": {
                    "gameStats": [
                        {
                            "score": 12.5,
                        },
                        {
                            "score": 13.5,
                        },
                    ]
                },
            },
        ]
    }
    assert SorareApiManager._get_ten_game_scores(player) == [11, 12, 13]


def test_get_game_count() -> None:
    player = {
        "upcomingGames": [
            {
                "gameWeek": 44,
            },
            {
                "gameWeek": 45,
            },
            {
                "gameWeek": 45,
            },
            {
                "gameWeek": 46,
            },
            {
                "gameWeek": 46,
            },
        ]
    }
    assert SorareApiManager._get_game_count(player, 45) == 2


def test_get_ten_game_custom_scores() -> None:
    player = {
        "latestFixtureStats": [
            {
                "fixture": {
                    "fixtureState": "opened",
                },
                "status": {"gameStats": []},
            },
            {
                "fixture": {
                    "fixtureState": "started",
                },
                "status": {
                    "gameStats": [
                        {
                            "score": 43,
                            "detailedStats": {
                                "points": 7,
                                "assists": 6,
                                "rebounds": 5,
                                "steals": 4,
                                "blocks": 3,
                                "made3PointFGs": 2,
                                "turnovers": 1,
                            },
                        }
                    ]
                },
            },
            {
                "fixture": {
                    "fixtureState": "closed",
                },
                "status": {"gameStats": []},
            },
            {
                "fixture": {
                    "fixtureState": "closed",
                },
                "status": {
                    "gameStats": [
                        {
                            "score": 0,
                            "detailedStats": {
                                "points": 0,
                                "assists": 0,
                                "rebounds": 0,
                                "steals": 0,
                                "blocks": 0,
                                "made3PointFGs": 0,
                                "turnovers": 0,
                            },
                        },
                        {
                            "score": 46,
                            "detailedStats": {
                                "points": 10,
                                "assists": 6,
                                "rebounds": 5,
                                "steals": 4,
                                "blocks": 3,
                                "made3PointFGs": 2,
                                "turnovers": 1,
                            },
                        },
                    ]
                },
            },
        ]
    }
    assert SorareApiManager._get_ten_game_custom_scores(player, CUSTOM_SCORING_DICT["normal"]) == [43, 0, 46]


# endregion


@app.command()
def run(custom_scoring_value: CustomScoringEnum) -> None:
    """example param: offense"""
    custom_scoring_key: str = custom_scoring_value.value  # type: ignore
    custom_scoring = CUSTOM_SCORING_DICT[custom_scoring_key]

    game_week = SorareApiManager.get_open_game_week()

    players, custom_players = SorareApiManager.get_all_my_players(game_week, custom_scoring)

    sorted_players = roster_mgr.get_players_sorted_by_profit(players)
    roster_mgr.output_to_console(sorted_players[:10])

    file_mgr.save_to_csv(players)
    file_mgr.save_to_csv(custom_players, CUSTOM_CSV_PATH)


@app.command()
def sim(name: str, game_count: int) -> None:
    matching_players = [player for player in file_mgr.load_from_csv() if name.lower() in player.name.lower()]
    output = "\n".join([f"{player.name}: {player_sim_mgr.player_simulation(player, game_count)}" for player in matching_players])
    print(output)


@app.command()
def team(team: str) -> None:
    players = file_mgr.load_from_csv()
    team_players = roster_mgr.get_players_from_team(players, team)
    sorted_team_players = roster_mgr.get_players_sorted_by_score(team_players)
    roster_mgr.output_to_console(sorted_team_players)


if __name__ == "__main__":
    """
    if update is done, then: add, bonus, run
    if update is not done, then: run/add, bonus
    """
    if CSV_PATH.exists():
        shutil.copy(CSV_PATH, CSV_PATH_BAK)
    if CUSTOM_CSV_PATH.exists():
        shutil.copy(CUSTOM_CSV_PATH, CUSTOM_CSV_PATH_BAK)

    app()
