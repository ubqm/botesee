import asyncio
from uuid import UUID

from pydantic import TypeAdapter

from src.clients.models.faceit.match_stats import (
    Round,
    RoundStats,
    TeamStats,
    MatchStatistics,
    Team,
    Player,
    PlayerStats,
)
from src.discord_bot.models.embed import NickEloStorage, PlayerStorage
from src.image_collectors.match_finished import MatchFinishedImCol
from src.web.models.events import MatchFinished


def match_finished_():
    finished = {
        "transaction_id": "47c8ade3-db36-4c0a-8471-7c340e9d7ac8",
        "event": "match_status_finished",
        "event_id": "6db8bfa8-0bbc-4a19-88b1-ea93ae8e3005",
        "third_party_id": "ad42c90b-45a9-49b6-8ab0-9c8662330543",
        "app_id": "4ef06a92-08ba-425e-bf12-c49c17d5ec7e",
        "timestamp": "2022-01-10T20:29:35Z",
        "retry_count": 0,
        "version": 1,
        "payload": {
            "id": "1-37a40c85-82ae-436d-9f90-fb7db5484033",
            "organizer_id": "faceit",
            "region": "EU",
            "game": "csgo",
            "version": 43,
            "entity": {
                "id": "a3c75828-7f0f-4940-adb9-994b4b389070",
                "name": "CS:GO 5v5 PREMIUM",
                "type": "matchmaking",
            },
            "teams": [
                {
                    "id": "8d5ead5d-b1b6-458d-93d0-1a0548d2de3f",
                    "name": "team_CJ-2k",
                    "type": "",
                    "avatar": "https://distribution.faceit-cdn.net/images/3911c173-368e-4dbd-8b1f-b0d19ade695a.jpeg",
                    "leader_id": "8d5ead5d-b1b6-458d-93d0-1a0548d2de3f",
                    "co_leader_id": "",
                    "roster": [
                        {
                            "id": "278790a2-1f08-4350-bd96-427f7dcc8722",
                            "nickname": "-NAPAD",
                            "avatar": "https://assets.faceit-cdn.net/avatars/278790a2-1f08-4350-bd96-427f7dcc8722_1583523957971.jpg",
                            "game_id": "76561198061461007",
                            "game_name": "-NAPAD`11 #ACIDHOUZE",
                            "game_skill_level": 10,
                            "membership": "",
                            "anticheat_required": True,
                        },
                        {
                            "id": "d0b7218c-a540-423f-960e-f6e9a8b3b10a",
                            "nickname": "-EcoCobra-",
                            "avatar": "https://assets.faceit-cdn.net/avatars/d0b7218c-a540-423f-960e-f6e9a8b3b10a_1633631507859.jpg",
                            "game_id": "76561198391731293",
                            "game_name": "yowai mo",
                            "game_skill_level": 10,
                            "membership": "",
                            "anticheat_required": True,
                        },
                        {
                            "id": "6dc2d3a1-8653-4ce6-8a2c-cb30122361e8",
                            "nickname": "S1non--",
                            "avatar": "https://distribution.faceit-cdn.net/images/72491042-bdd6-4fc5-a8ba-e7fea300ac88.jpeg",
                            "game_id": "76561198251305342",
                            "game_name": "S1non",
                            "game_skill_level": 10,
                            "membership": "",
                            "anticheat_required": True,
                        },
                        {
                            "id": "131b67d6-3e3a-4a79-a4bc-7d73ea404c8e",
                            "nickname": "Deokishisu",
                            "avatar": "https://distribution.faceit-cdn.net/images/110c80b9-1f38-4426-9429-d6edeaa150c1.jpeg",
                            "game_id": "76561199174381757",
                            "game_name": "xGOD",
                            "game_skill_level": 10,
                            "membership": "",
                            "anticheat_required": True,
                        },
                        {
                            "id": "8d5ead5d-b1b6-458d-93d0-1a0548d2de3f",
                            "nickname": "CJ-2k",
                            "avatar": "https://distribution.faceit-cdn.net/images/3911c173-368e-4dbd-8b1f-b0d19ade695a.jpeg",
                            "game_id": "76561199006885634",
                            "game_name": "asd",
                            "game_skill_level": 10,
                            "membership": "",
                            "anticheat_required": True,
                        },
                    ],
                    "substitutions": 0,
                    "substitutes": None,
                },
                {
                    "id": "f8580374-5c09-43bc-bef2-463f1fde9aff",
                    "name": "team_sinnopsyy",
                    "type": "",
                    "avatar": "https://distribution.faceit-cdn.net/images/62a8416a-7cba-44b9-bab6-c5430f992eb9.jpeg",
                    "leader_id": "f8580374-5c09-43bc-bef2-463f1fde9aff",
                    "co_leader_id": "",
                    "roster": [
                        {
                            "id": "f8580374-5c09-43bc-bef2-463f1fde9aff",
                            "nickname": "sinnopsyy",
                            "avatar": "https://distribution.faceit-cdn.net/images/62a8416a-7cba-44b9-bab6-c5430f992eb9.jpeg",
                            "game_id": "76561198165327895",
                            "game_name": "sinnopsy=D",
                            "game_skill_level": 10,
                            "membership": "",
                            "anticheat_required": True,
                        },
                        {
                            "id": "440c0bf9-028a-4234-932c-3cb53e285851",
                            "nickname": "katNine",
                            "avatar": "https://distribution.faceit-cdn.net/images/c44d20cc-b2aa-4129-a9d4-5bbeb382d42e.jpeg",
                            "game_id": "76561198025532625",
                            "game_name": "k",
                            "game_skill_level": 10,
                            "membership": "",
                            "anticheat_required": True,
                        },
                        {
                            "id": "1b4e291a-c1c9-48c1-8738-5fda9a109151",
                            "nickname": "Coopah-iwnl-",
                            "avatar": "https://assets.faceit-cdn.net/avatars/1b4e291a-c1c9-48c1-8738-5fda9a109151_1626554809867.jpg",
                            "game_id": "76561198137616643",
                            "game_name": "I only frag when im on drugs❤",
                            "game_skill_level": 10,
                            "membership": "",
                            "anticheat_required": True,
                        },
                        {
                            "id": "e284326a-04c2-41b2-8e1b-851e9b5f9761",
                            "nickname": "-ReGnZ-",
                            "avatar": "https://assets.faceit-cdn.net/avatars/e284326a-04c2-41b2-8e1b-851e9b5f9761_1550964104764.jpg",
                            "game_id": "76561198070260050",
                            "game_name": "ReGnZ",
                            "game_skill_level": 10,
                            "membership": "",
                            "anticheat_required": True,
                        },
                        {
                            "id": "0b21055e-a2a6-4a4e-a1b8-3691352ce8f5",
                            "nickname": "faqazy",
                            "avatar": "https://distribution.faceit-cdn.net/images/49e275b8-c2e7-419b-a0dc-389dc21d7166.jpeg",
                            "game_id": "76561198799957222",
                            "game_name": "᠌ ᠌ ᠌᠌ ᠌ ᠌ ᠌ ᠌",
                            "game_skill_level": 10,
                            "membership": "",
                            "anticheat_required": True,
                        },
                    ],
                    "substitutions": 0,
                    "substitutes": None,
                },
            ],
            "created_at": "2022-01-10T19:46:45Z",
            "updated_at": "2022-01-10T20:29:35Z",
            "started_at": "2022-01-10T19:51:43Z",
            "finished_at": "2022-01-10T20:29:35Z",
        },
    }
    return MatchFinished(**finished)


def match_stats_() -> MatchStatistics:
    data = {
        "rounds": [
            Round(
                best_of=2,
                competition_id=None,
                game_id="csgo",
                game_mode="5v5",
                match_id="1-37a40c85-82ae-436d-9f90-fb7db5484033",
                match_round=1,
                played=1,
                round_stats=RoundStats(
                    score="16 / 9",
                    region="EU",
                    rounds=25,
                    map="de_mirage",
                    winner=UUID("8d5ead5d-b1b6-458d-93d0-1a0548d2de3f"),
                ),
                teams=[
                    Team(
                        team_id=UUID("8d5ead5d-b1b6-458d-93d0-1a0548d2de3f"),
                        premade=False,
                        team_stats=TeamStats(
                            team="team_CJ-2k",
                            team_win=True,
                            team_headshots=11.8,
                            first_half_score=8,
                            second_half_score=8,
                            overtime_score=0,
                            final_score=16,
                        ),
                        players=[
                            Player(
                                player_id=UUID("278790a2-1f08-4350-bd96-427f7dcc8722"),
                                nickname="-NAPAD",
                                player_stats=PlayerStats(
                                    kills=21,
                                    assists=3,
                                    deaths=9,
                                    kd_ratio=2.33,
                                    kr_ratio=0.84,
                                    mvps=3,
                                    headshots=11,
                                    headshots_p=52,
                                    tripple=2,
                                    quadro=0,
                                    ace=0,
                                    result=True,
                                ),
                            ),
                            Player(
                                player_id=UUID("d0b7218c-a540-423f-960e-f6e9a8b3b10a"),
                                nickname="-EcoCobra-",
                                player_stats=PlayerStats(
                                    kills=17,
                                    assists=3,
                                    deaths=18,
                                    kd_ratio=0.94,
                                    kr_ratio=0.68,
                                    mvps=2,
                                    headshots=10,
                                    headshots_p=59,
                                    tripple=1,
                                    quadro=0,
                                    ace=0,
                                    result=True,
                                ),
                            ),
                            Player(
                                player_id=UUID("6dc2d3a1-8653-4ce6-8a2c-cb30122361e8"),
                                nickname="S1non--",
                                player_stats=PlayerStats(
                                    kills=20,
                                    assists=3,
                                    deaths=12,
                                    kd_ratio=1.67,
                                    kr_ratio=0.8,
                                    mvps=2,
                                    headshots=10,
                                    headshots_p=50,
                                    tripple=2,
                                    quadro=0,
                                    ace=0,
                                    result=True,
                                ),
                            ),
                            Player(
                                player_id=UUID("131b67d6-3e3a-4a79-a4bc-7d73ea404c8e"),
                                nickname="Deokishisu",
                                player_stats=PlayerStats(
                                    kills=17,
                                    assists=3,
                                    deaths=16,
                                    kd_ratio=1.06,
                                    kr_ratio=0.68,
                                    mvps=2,
                                    headshots=11,
                                    headshots_p=65,
                                    tripple=0,
                                    quadro=1,
                                    ace=0,
                                    result=True,
                                ),
                            ),
                            Player(
                                player_id=UUID("8d5ead5d-b1b6-458d-93d0-1a0548d2de3f"),
                                nickname="CJ-2k",
                                player_stats=PlayerStats(
                                    kills=30,
                                    assists=2,
                                    deaths=15,
                                    kd_ratio=2.0,
                                    kr_ratio=1.2,
                                    mvps=7,
                                    headshots=17,
                                    headshots_p=57,
                                    tripple=2,
                                    quadro=0,
                                    ace=0,
                                    result=True,
                                ),
                            ),
                        ],
                    ),
                    Team(
                        team_id=UUID("f8580374-5c09-43bc-bef2-463f1fde9aff"),
                        premade=False,
                        team_stats=TeamStats(
                            team="team_sinnopsyy",
                            team_win=False,
                            team_headshots=7.6,
                            first_half_score=7,
                            second_half_score=2,
                            overtime_score=0,
                            final_score=9,
                        ),
                        players=[
                            Player(
                                player_id=UUID("f8580374-5c09-43bc-bef2-463f1fde9aff"),
                                nickname="sinnopsyy",
                                player_stats=PlayerStats(
                                    kills=19,
                                    assists=3,
                                    deaths=23,
                                    kd_ratio=0.83,
                                    kr_ratio=0.76,
                                    mvps=5,
                                    headshots=13,
                                    headshots_p=68,
                                    tripple=2,
                                    quadro=0,
                                    ace=0,
                                    result=False,
                                ),
                            ),
                            Player(
                                player_id=UUID("440c0bf9-028a-4234-932c-3cb53e285851"),
                                nickname="katNine",
                                player_stats=PlayerStats(
                                    kills=11,
                                    assists=1,
                                    deaths=23,
                                    kd_ratio=0.48,
                                    kr_ratio=0.44,
                                    mvps=1,
                                    headshots=6,
                                    headshots_p=55,
                                    tripple=0,
                                    quadro=0,
                                    ace=0,
                                    result=False,
                                ),
                            ),
                            Player(
                                player_id=UUID("1b4e291a-c1c9-48c1-8738-5fda9a109151"),
                                nickname="Coopah-iwnl-",
                                player_stats=PlayerStats(
                                    kills=14,
                                    assists=0,
                                    deaths=20,
                                    kd_ratio=0.7,
                                    kr_ratio=0.56,
                                    mvps=1,
                                    headshots=7,
                                    headshots_p=50,
                                    tripple=1,
                                    quadro=0,
                                    ace=0,
                                    result=False,
                                ),
                            ),
                            Player(
                                player_id=UUID("e284326a-04c2-41b2-8e1b-851e9b5f9761"),
                                nickname="-ReGnZ-",
                                player_stats=PlayerStats(
                                    kills=10,
                                    assists=1,
                                    deaths=19,
                                    kd_ratio=0.53,
                                    kr_ratio=0.4,
                                    mvps=1,
                                    headshots=3,
                                    headshots_p=30,
                                    tripple=0,
                                    quadro=0,
                                    ace=0,
                                    result=False,
                                ),
                            ),
                            Player(
                                player_id=UUID("0b21055e-a2a6-4a4e-a1b8-3691352ce8f5"),
                                nickname="faqazy",
                                player_stats=PlayerStats(
                                    kills=16,
                                    assists=0,
                                    deaths=20,
                                    kd_ratio=0.8,
                                    kr_ratio=0.64,
                                    mvps=1,
                                    headshots=9,
                                    headshots_p=56,
                                    tripple=1,
                                    quadro=0,
                                    ace=0,
                                    result=False,
                                ),
                            ),
                        ],
                    ),
                ],
            )
        ]
    }
    return MatchStatistics(**data)


async def main():
    mf = match_finished_()
    statistics = TypeAdapter(MatchStatistics).validate_json(
        '{"rounds":[{"best_of":2,"competition_id":null,"game_id":"cs2","game_mode":"5v5","match_id":"1-37a40c85-82ae-436d-9f90-fb7db5484033","match_round":1,"played":1,"round_stats":{"Score":"16 / 9","Region":"EU","Rounds":25,"Map":"de_mirage","Winner":"8d5ead5d-b1b6-458d-93d0-1a0548d2de3f"},"teams":[{"team_id":"8d5ead5d-b1b6-458d-93d0-1a0548d2de3f","premade":false,"team_stats":{"Team":"team_CJ-2k","Team Win":true,"Team Headshots":11.8,"First Half Score":8,"Second Half Score":8,"Overtime score":0,"Final Score":16},"players":[{"player_id":"278790a2-1f08-4350-bd96-427f7dcc8722","nickname":"-NAPAD","player_stats":{"Kills":21,"Assists":3,"Deaths":9,"K/D Ratio":2.33,"K/R Ratio":0.84,"MVPs":3,"Headshots":11,"Headshots %":52,"Triple Kills":2,"Quadro Kills":0,"Penta Kills":0,"Result":true}},{"player_id":"d0b7218c-a540-423f-960e-f6e9a8b3b10a","nickname":"-EcoCobra-","player_stats":{"Kills":17,"Assists":3,"Deaths":18,"K/D Ratio":0.94,"K/R Ratio":0.68,"MVPs":2,"Headshots":10,"Headshots %":59,"Triple Kills":1,"Quadro Kills":0,"Penta Kills":0,"Result":true}},{"player_id":"6dc2d3a1-8653-4ce6-8a2c-cb30122361e8","nickname":"S1non--","player_stats":{"Kills":20,"Assists":3,"Deaths":12,"K/D Ratio":1.67,"K/R Ratio":0.8,"MVPs":2,"Headshots":10,"Headshots %":50,"Triple Kills":2,"Quadro Kills":0,"Penta Kills":0,"Result":true}},{"player_id":"131b67d6-3e3a-4a79-a4bc-7d73ea404c8e","nickname":"Deokishisu","player_stats":{"Kills":17,"Assists":3,"Deaths":16,"K/D Ratio":1.06,"K/R Ratio":0.68,"MVPs":2,"Headshots":11,"Headshots %":65,"Triple Kills":0,"Quadro Kills":1,"Penta Kills":0,"Result":true}},{"player_id":"8d5ead5d-b1b6-458d-93d0-1a0548d2de3f","nickname":"CJ-2k","player_stats":{"Kills":30,"Assists":2,"Deaths":15,"K/D Ratio":2.0,"K/R Ratio":1.2,"MVPs":7,"Headshots":17,"Headshots %":57,"Triple Kills":2,"Quadro Kills":0,"Penta Kills":0,"Result":true}}]},{"team_id":"f8580374-5c09-43bc-bef2-463f1fde9aff","premade":false,"team_stats":{"Team":"team_sinnopsyy","Team Win":false,"Team Headshots":7.6,"First Half Score":7,"Second Half Score":2,"Overtime score":0,"Final Score":9},"players":[{"player_id":"f8580374-5c09-43bc-bef2-463f1fde9aff","nickname":"sinnopsyy","player_stats":{"Kills":19,"Assists":3,"Deaths":23,"K/D Ratio":0.83,"K/R Ratio":0.76,"MVPs":5,"Headshots":13,"Headshots %":68,"Triple Kills":2,"Quadro Kills":0,"Penta Kills":0,"Result":false}},{"player_id":"440c0bf9-028a-4234-932c-3cb53e285851","nickname":"katNine","player_stats":{"Kills":11,"Assists":1,"Deaths":23,"K/D Ratio":0.48,"K/R Ratio":0.44,"MVPs":1,"Headshots":6,"Headshots %":55,"Triple Kills":0,"Quadro Kills":0,"Penta Kills":0,"Result":false}},{"player_id":"1b4e291a-c1c9-48c1-8738-5fda9a109151","nickname":"Coopah-iwnl-","player_stats":{"Kills":14,"Assists":0,"Deaths":20,"K/D Ratio":0.7,"K/R Ratio":0.56,"MVPs":1,"Headshots":7,"Headshots %":50,"Triple Kills":1,"Quadro Kills":0,"Penta Kills":0,"Result":false}},{"player_id":"e284326a-04c2-41b2-8e1b-851e9b5f9761","nickname":"-ReGnZ-","player_stats":{"Kills":10,"Assists":1,"Deaths":19,"K/D Ratio":0.53,"K/R Ratio":0.4,"MVPs":1,"Headshots":3,"Headshots %":30,"Triple Kills":0,"Quadro Kills":0,"Penta Kills":0,"Result":false}},{"player_id":"0b21055e-a2a6-4a4e-a1b8-3691352ce8f5","nickname":"faqazy","player_stats":{"Kills":16,"Assists":0,"Deaths":20,"K/D Ratio":0.8,"K/R Ratio":0.64,"MVPs":1,"Headshots":9,"Headshots %":56,"Triple Kills":1,"Quadro Kills":0,"Penta Kills":0,"Result":false}}]}]}]}'
    )
    mf_imcol = MatchFinishedImCol(
        mf,
        statistics.rounds[0],
        NickEloStorage(
            players=[
                PlayerStorage(nickname="-NAPAD", elo=3700),
                PlayerStorage(nickname="-EcoCobra-", elo=3120),
                PlayerStorage(nickname="S1non--", elo=3670),
                PlayerStorage(nickname="Deokishisu", elo=2260),
                PlayerStorage(nickname="CJ-2k", elo=4300),
                PlayerStorage(nickname="sinnopsyy", elo=5220),
                PlayerStorage(nickname="katNine", elo=2720),
                PlayerStorage(nickname="Coopah-iwnl-", elo=4150),
                PlayerStorage(nickname="-ReGnZ-", elo=2580),
                PlayerStorage(nickname="faqazy", elo=3630),
            ]
        ),
    )
    image = await mf_imcol.collect_image()
    image.show()


if __name__ == "__main__":
    asyncio.run(main())
