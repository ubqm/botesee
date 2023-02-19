import asyncio
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from tortoise import Tortoise, run_async
from tortoise.expressions import Subquery

from bot.db.models_tortoise import Player, Elo
from env_variables import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

NAPAD = "278790a2-1f08-4350-bd96-427f7dcc8722"
MORZY = "18e2a663-9e20-4db9-8b29-3c3cbdff30ac"


async def init():
    await Tortoise.init(
        db_url=f'postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}',
        modules={'models': ['db.models']}
    )

    # await Tortoise.generate_schemas()


async def get_players():
    return await Player.all()


async def get_elo_by_player():
    napad_matches = Subquery(
        Elo.filter(
            player=NAPAD
        ).values_list(
            'match_id',
            flat=True
        )
    )

    return await Elo.filter(
        player=MORZY,
        match__id__in=napad_matches,
        match__date__gte=datetime.datetime(2022, 5, 1)
    ).values('match__date', 'elo')


# 278790a2-1f08-4350-bd96-427f7dcc8722 NAPAD
# 18e2a663-9e20-4db9-8b29-3c3cbdff30ac MORZY


async def main():
    res1 = await get_elo_by_player()
    # res2 = await get_elo_with_other_player()
    gen = (x for x in res1)
    x, y = [], []
    for obj in gen:
        x.append(obj['match__date'])
        y.append(obj['elo'])
    # print(x, y)
    sns.set_theme(style="darkgrid")
    sns.lineplot(x=x, y=y, ls='-')
    plt.gcf().autofmt_xdate()
    plt.title('MORZY')
    plt.xlabel('Date')
    plt.ylabel('Elo')
    plt.show()


if __name__ == '__main__':
    run_async(init())
    asyncio.run(main())

    # plt.plot(data=[x, y])
    # plt.show()
