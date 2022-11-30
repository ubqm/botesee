from tortoise import Tortoise, run_async
from env_variables import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME


async def init():
    await Tortoise.init(
        db_url=f'postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}',
        modules={'models': ['db.models']}
    )

    # await Tortoise.generate_schemas()


if __name__ == '__main__':
    run_async(init())
