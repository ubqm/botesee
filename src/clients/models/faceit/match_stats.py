from uuid import UUID

from pydantic import BaseModel, Field


class RoundStats(BaseModel):
    score: str = Field(alias="Score")
    region: str = Field(alias="Region")
    rounds: int = Field(alias="Rounds")
    map: str = Field(alias="Map")
    winner: UUID = Field(alias="Winner")


class PlayerStats(BaseModel):
    ace: int = Field(alias="Penta Kills")
    adr: float = Field(alias="ADR")
    assists: int = Field(alias="Assists")
    clutch_kills: int = Field(alias="Clutch Kills")
    count_1v1: int = Field(alias="1v1Count")
    count_1v2: int = Field(alias="1v2Count")
    damage: int = Field(alias="Damage")
    deaths: int = Field(alias="Deaths")
    double_kills: int = Field(alias="Double Kills")
    entry_count: int = Field(alias="Entry Count")
    entry_wins: int = Field(alias="Entry Wins")
    enemies_flashed: int = Field(alias="Enemies Flashed")
    enemies_flashed_per_round: float = Field(
        alias="Enemies Flashed per Round in a Match"
    )
    first_kills: int = Field(alias="First Kills")
    flash_count: int = Field(alias="Flash Count")
    flash_success_rate: float = Field(alias="Flash Success Rate per Match")
    flash_successes: int = Field(alias="Flash Successes")
    flashes_per_round: float = Field(alias="Flashes per Round in a Match")
    headshots: int = Field(alias="Headshots")
    headshots_p: int = Field(alias="Headshots %")
    kd_ratio: float = Field(alias="K/D Ratio")
    knife_kills: int = Field(alias="Knife Kills")
    kills: int = Field(alias="Kills")
    kr_ratio: float = Field(alias="K/R Ratio")
    match_1v1_winrate: float = Field(alias="Match 1v1 Win Rate")
    match_1v2_winrate: float = Field(alias="Match 1v2 Win Rate")
    match_entry_rate: float = Field(alias="Match Entry Rate")
    match_entry_success_rate: float = Field(alias="Match Entry Success Rate")
    mvps: int = Field(alias="MVPs")
    pistol_kills: int = Field(alias="Pistol Kills")
    quadro: int = Field(alias="Quadro Kills")
    result: bool = Field(alias="Result")
    sniper_kill_rate: float = Field(alias="Sniper Kill Rate per Match")
    sniper_kill_rate_per_round: float = Field(alias="Sniper Kill Rate per Round")
    sniper_kills: int = Field(alias="Sniper Kills")
    tripple: int = Field(alias="Triple Kills")
    utility_count: int = Field(alias="Utility Count")
    utility_damage: int = Field(alias="Utility Damage")
    utility_damage_per_round: float = Field(alias="Utility Damage per Round in a Match")
    utility_damage_success_rate: float = Field(
        alias="Utility Damage Success Rate per Match"
    )
    utility_enemies: int = Field(alias="Utility Enemies")
    utility_success_rate: float = Field(alias="Utility Success Rate per Match")
    utility_successes: int = Field(alias="Utility Successes")
    utility_usage_per_round: float = Field(alias="Utility Usage per Round")
    wins_1v1: int = Field(alias="1v1Wins")
    wins_1v2: int = Field(alias="1v2Wins")
    zeus_kills: int = Field(alias="Zeus Kills")


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

    def get_enemy_players(self, current_player_id: UUID) -> list[Player]:
        team0_player_ids = [player.player_id for player in self.teams[0].players]
        enemy_team_idx: int = 0 if current_player_id in team0_player_ids else 1

        if not enemy_team_idx:
            return []

        return self.teams[enemy_team_idx].players


class MatchStatistics(BaseModel):
    rounds: list[Round] = Field(default_factory=list)
