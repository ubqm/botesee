import random
import uuid
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import sessionmaker
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select


class Elo(SQLModel, table=True):
    match: UUID = Field(foreign_key="match.id", primary_key=True)
    player: UUID = Field(foreign_key="player.id", primary_key=True)
    elo: int

    # players: list["Player"] = Relationship(back_populates="elo", sa_relationship_kwargs={"cascade": "all"})
    # matches: list["Match"] = Relationship(back_populates="elo", sa_relationship_kwargs={"cascade": "all"})


class Player(SQLModel, table=True):
    id: UUID = Field(primary_key=True, default_factory=uuid.uuid4)

    matches: list["Match"] = Relationship(back_populates="players", link_model=Elo)


class Match(SQLModel, table=True):
    id: UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    date: datetime = Field(default=datetime.now(tz=timezone.utc))

    players: list["Player"] = Relationship(back_populates="matches", link_model=Elo)


con_string = "sqlmodel:password@127.0.0.1:5433/sqlmodel"
sqlite_url = f"postgresql://{con_string}"

engine = create_engine(sqlite_url, echo=True)
session_ = sessionmaker(bind=engine)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    with Session(engine) as session:
        players = [Player() for _ in range(9)]
        stmt = select(Match).where(Match.id == "652ce312-00be-448e-b5d4-25595acfabc5")
        print(stmt)
        result = session.execute(stmt)
        print(result)
        # print(result.scalar_one())
        match = Match.from_orm(result.scalar_one())
        print(f"{match = }")
        elos = [Elo(match=match.id, player=player.id, elo=random.randint(2000, 2500)) for player in players]
        for elo in elos:
            print(elo)
        session.add_all(players)
        session.commit()
        session.add_all(elos)
        session.commit()
