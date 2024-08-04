from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src import conf

engine = create_async_engine(conf.db_string)
session_maker = async_sessionmaker(engine)


class Base(DeclarativeBase):
    pass
