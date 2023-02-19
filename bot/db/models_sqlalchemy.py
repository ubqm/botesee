import os
from datetime import datetime
from uuid import UUID
from pytz import utc
from sqlalchemy import Column, create_engine, DateTime, ForeignKey, Integer, select
from sqlalchemy.orm import registry, relationship, Mapped, Session
from sqlalchemy import UUID as saUUID



mapper_registry = registry()

# session = Session(engine)


@mapper_registry.mapped
class Elo:
    __tablename__ = 'elos'

    player_id: UUID = Column(saUUID, ForeignKey('players.id'), primary_key=True)
    match_id: UUID = Column(saUUID, ForeignKey('matches.id'), primary_key=True)
    elo: int = Column(Integer)
    player: Mapped['Player'] = relationship(back_populates='elos')
    match: Mapped['Match'] = relationship(back_populates='elos')


@mapper_registry.mapped
class Player:
    __tablename__ = 'players'

    id: Mapped[UUID] = Column(saUUID, primary_key=True)

    elos: Mapped[list[Elo]] = relationship(back_populates='player')
    matches: Mapped[list["Match"]] = relationship(secondary="elos", back_populates='players')


@mapper_registry.mapped
class Match:
    __tablename__ = 'matches'

    id: Mapped[UUID] = Column(saUUID, primary_key=True)
    date: Mapped[datetime] = Column(DateTime, default=datetime.now(tz=utc))

    elos: Mapped[list[Elo]] = relationship(back_populates='match')
    players: Mapped[list[Player]] = relationship(secondary="elos", back_populates='matches')


def create_db_and_tables():
    mapper_registry.metadata.create_all(engine)


if __name__ == '__main__':
    con_string = "postgresql://sqlmodel:password@127.0.0.1:5433/sqlmodel"
    engine = create_engine(con_string, echo=True)
    # mapper_registry.metadata.drop_all(engine)
    # create_db_and_tables()
    with Session(engine) as session:
        stmt = select(Match)
        result: Match = session.execute(stmt).scalar_one()
        print(result.players[0].id)
        # player = Player(id=UUID(bytes=os.urandom(16)))
        # elo = Elo(elo=42)
        # elo.match = Match(id=UUID(bytes=os.urandom(16)))
        # player.elos.append(elo)
        # session.add(player)
        # session.commit()
