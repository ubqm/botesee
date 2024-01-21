from uuid import UUID

from pydantic import BaseModel, Field


class LifetimeStats(BaseModel):
    total_matches: int = Field(alias="Matches", description="Total number of matches")
    longest_win_streak: int = Field(alias="Longest Win Streak")
    recent_results: list[bool] = Field(alias="Recent Results")
    avg_hs: int = Field(alias="Average Headshots %", description="From 0 to 100")
    avg_kd: float = Field(alias="Average K/D Ratio")
    total_wins: int = Field(alias="Wins", description="Total number of wins")
    total_headshots: int = Field(alias="Total Headshots %", description="Total number of Headshots (Not percentage)")
    winrate: int = Field(alias="Win Rate %", description="from 0 to 100")
    current_win_streak: int = Field(alias="Current Win Streak")
    total_kd_p: float = Field(alias="K/D Ratio", description="Strange number, don't use it")


class SegmentStats(BaseModel):
    avg_hs_frags_per_match: float = Field(alias="Headshots per Match", description="Avg HS frags per match")
    total_deaths: int = Field(alias="Deaths")
    total_kr: float = Field(alias="K/R Ratio", description="Strange number, don't use it")
    total_triple: int = Field(alias="Triple Kills")
    total_hs_p: int = Field(alias="Total Headshots %", description="Total number of Headshots (Not percentage)")
    total_kills: int = Field(alias="Kills")
    total_rounds: int = Field(alias="Rounds")
    total_wins: int = Field(alias="Wins")
    avg_kd: float = Field(alias="Average K/D Ratio")
    windrate: int = Field(alias="Win Rate %", description="From 0 to 100")
    avg_kr: float = Field(alias="Average K/R Ratio")
    total_hs: int = Field(alias="Headshots")
    total_assists: int = Field(alias="Assists")
    avk_kills: float = Field(alias="Average Kills")
    avg_quadro: float = Field(alias="Average Quadro Kills")
    avg_ace: float = Field(alias="Average Penta Kills")
    total_mvp: int = Field(alias="MVPs")
    total_ace: int = Field(alias="Penta Kills")
    total_matches: int = Field(alias="Matches")
    avg_mvp: float = Field(alias="Average MVPs")
    avg_assists: float = Field(alias="Average Assists")
    kd_ratio_p: float = Field(alias="K/D Ratio", description="Strange number, don't use it")
    total_quadro: int = Field(alias="Quadro Kills")
    avg_deaths: float = Field(alias="Average Deaths")
    avg_hs: int = Field(alias="Average Headshots %", description="From 0 to 100")
    avg_triple: float = Field(alias="Average Triple Kills")


class Segment(BaseModel):
    stats: SegmentStats
    type: str  # Map
    mode: str  # 5v5
    label: str  # de_inferno
    img_small: str
    img_regular: str


class PlayerGameStats(BaseModel):
    player_id: UUID
    game_id: str  # csgo
    lifetime: LifetimeStats
    segments: list[Segment]
