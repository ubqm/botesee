from tortoise import fields
from tortoise.models import Model


class Player(Model):
    id = fields.CharField(max_length=255, pk=True)

    def __str__(self) -> str:
        return self.id

    class Meta:
        table = "players"


class Match(Model):
    id = fields.CharField(max_length=255, pk=True)
    date = fields.DatetimeField()

    def __str__(self) -> str:
        return f"{self.id} at {self.date}"

    class Meta:
        table = "matches"


class Elo(Model):
    id = fields.IntField(pk=True)
    match = fields.ForeignKeyField("models.Match", on_delete="CASCADE")
    player = fields.ForeignKeyField("models.Player", on_delete="CASCADE")
    elo = fields.IntField()

    def __str__(self):
        return f"{self.player} in {self.match} with {self.elo} elo"

    class Meta:
        table = "elos"
