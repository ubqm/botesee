from bot import conf
from bot.clients.rabbit import RabbitClient


def get_rabbit() -> RabbitClient:
    return RabbitClient(conf.RABBIT_HOST, conf.RABBIT_PORT, conf.RABBIT_USER, conf.RABBIT_PASSWORD)
