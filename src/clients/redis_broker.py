from faststream.redis.broker import RedisBroker

from src import conf

redis_broker = RedisBroker(conf.redis_string)
