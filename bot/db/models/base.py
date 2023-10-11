from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from bot import conf

engine = create_async_engine(conf.pg_string)
Session = async_sessionmaker(engine)


class Base(DeclarativeBase):
    pass
