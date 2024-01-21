from uuid import UUID

from pydantic import BaseModel, Field


class RoundStats(BaseModel):
    score: str = Field(alias="Score")
    region: str = Field(alias="Region")
    rounds: int = Field(alias="Rounds")
    map: str = Field(alias="Map")
    winner: UUID = Field(alias="Winner")


class PlayerStats(BaseModel):
    kills: int = Field(alias="Kills")
    assists: int = Field(alias="Assists")
    deaths: int = Field(alias="Deaths")
    kd_ratio: float = Field(alias="K/D Ratio")
    kr_ratio: float = Field(alias="K/R Ratio")
    mvps: int = Field(alias="MVPs")
    headshots: int = Field(alias="Headshots")
    headshots_p: int = Field(alias="Headshots %", description="int from 0 to 100")
    tripple: int = Field(alias="Triple Kills")
    quadro: int = Field(alias="Quadro Kills")
    ace: int = Field(alias="Penta Kills")
    result: bool = Field(alias="Result")


class Player(BaseModel):
    player_id: UUID
    nickname: str
    player_stats: PlayerStats


class TeamStats(BaseModel):
    team: str = Field(alias="Team")
    team_win: bool = Field(alias="Team Win")
    team_headshots: float = Field(alias="Team Headshots")
    first_half_score: int = Field(alias="First Half Score")
    second_half_score: int = Field(alias="Second Half Score")
    overtime_score: int = Field(alias="Overtime score")
    final_score: int = Field(alias="Final Score")


class Team(BaseModel):
    team_id: UUID
    premade: bool
    team_stats: TeamStats
    players: list[Player]


class Round(BaseModel):
    best_of: int
    competition_id: str | None = None
    game_id: str
    game_mode: str
    match_id: str
    match_round: int
    played: int
    round_stats: RoundStats
    teams: list[Team]

    def has_overtime(self) -> bool:
        return any(
            (
                self.teams[0].team_stats.overtime_score,
                self.teams[1].team_stats.overtime_score,
            )
        )

    def get_player_stats(self, player_id: UUID) -> PlayerStats | None:
        for team in self.teams:
            for player in team.players:
                if player.player_id == player_id:
                    return player.player_stats
        return None


class MatchStatistics(BaseModel):
    rounds: list[Round]
