from pydantic import BaseModel


class PlayerStorage(BaseModel):
    nickname: str
    elo: int
    subscriber: bool = False


class NickEloStorage(BaseModel):
    players: list[PlayerStorage]

    def get_discord_nicknames(self, sep: str = "\n") -> str:
        nicknames = [
            f"{'-> ' if player.subscriber else ''}[{player.nickname}](https://www.faceit.com/en/players/{player.nickname})"
            for player in self.players
        ]
        return sep.join(nicknames)

    def get_discord_elos(self, sep: str = "\n") -> str:
        return sep.join([str(player.elo) for player in self.players])

    def list_nicknames(self) -> list[str]:
        return [player.nickname for player in self.players]

    def list_elos(self) -> list[int]:
        return [player.elo for player in self.players]

    def __getitem__(self, nickname: str) -> PlayerStorage:
        for player in self.players:
            if player.nickname == nickname:
                return player
        return PlayerStorage(nickname="Not Found", elo=0)

    def get_dict(self) -> dict[str, int]:
        return {player.nickname: player.elo for player in self.players}

    def get_avg_elo(self) -> int:
        return int(sum([player.elo for player in self.players]) / len(self.players))
