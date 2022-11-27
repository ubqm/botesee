import asyncio

from db.init import init
from models import Player, Match, Elo
from tortoise import run_async
import csv


def transfer_matches():
    with open("../matches.csv", mode="r") as matches_file:
        matches_reader = csv.reader(matches_file)
        return [x for x in matches_reader]


def transfer_players():
    with open("../players.csv", mode="r") as players_file:
        players_reader = csv.reader(players_file)
        return [x for x in players_reader]


def transfer_elos():
    with open("../elos.csv", mode="r") as elos_file:
        elos_reader = csv.reader(elos_file)
        return [x for x in elos_reader]


async def get_player_by_id(pid: str):
    player = await Player.get(
        id=pid
    )
    return player


if __name__ == '__main__':
    run_async(init())
    old_matches = transfer_matches()
    old_players = transfer_players()
    old_elos = transfer_elos()
    for match in old_matches:
        run_async(
            Match.create(
                id=match[1],
                date=match[2],
            )
        )
    print("matches transfer ended")
    for player in old_players:
        run_async(
            Player.create(
                id=player[1]
            )
        )
    print("players transfer ended")
    for elo in old_elos:  # [player_id, match_id, elo]  e.g. [1, 57, 3567]
        # print(elo)
        player_id = elo[0]
        match_id = elo[1]
        # print(f"{player_id = }, {match_id = }")
        actual_pid = None
        actual_mid = None
        for match in old_matches:
            # print(f"{match = }")
            if match[0] == match_id:
                actual_mid = match[1]
                # print(f"{actual_mid = }")
                break
        for player in old_players:
            # print(f"{player = }")
            if player[0] == player_id:
                actual_pid = player[1]
                # print(f"{actual_pid = }")
                break
        # print(f"{actual_pid = }, {actual_mid = }")
        run_async(
            Elo.create(
                player_id=actual_pid,
                match_id=actual_mid,
                elo=elo[2]
            )
        )
        print(f"created {elo}")
