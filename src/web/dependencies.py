from src import conf
from src.clients.rabbit import RabbitClient


async def get_rabbit() -> RabbitClient:
    return RabbitClient(
        conf.RABBIT_HOST, conf.RABBIT_PORT, conf.RABBIT_USER, conf.RABBIT_PASSWORD
    )
