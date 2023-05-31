from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from bot.discord_bot import conf

engine = create_engine(
    f"postgresql://{conf.DB_USER}:{conf.DB_PASSWORD}@localhost:{conf.DB_PORT}/{conf.DB_NAME}", echo=True
)

Session = sessionmaker(engine)


class Base(DeclarativeBase):
    pass
