# import asyncio
#
# import discord
# import os
# from threading import Thread
# from functools import partial
#
# from application.db.init import init
#
# from application.discord_bot.client import DiscordClient
# from application.web.main import app
# from database import db_fetch_data
#
#
# async def main1():
#     loop = asyncio.get_running_loop()
#     intents = discord.Intents.all()
#     discord_bot = DiscordClient(intents=intents, faceit_channel_id=828940900033626113)
#
#
#
#     port = int(os.environ.get("PORT", 5000))
#     print(f"variable port:{port}")
#     # uvicorn.run(app, host="0.0.0.0", port=8001)
#
#     # await init()
#     # t1 = Thread(target=partial_run)
#     # t1.start()
#     # await bot_client.start(discord_token)
import asyncio
import json

import pika
from pydantic import parse_obj_as

from application.web.models.events import WebhookMatch


async def func1():
    while True:
        print(1)

async def func2():
    while True:
        print(2)

async def main(loop):
    loop.create_task(await func1())
    loop.create_task(await func2())
    # asyncio.create_task(func1())
    # asyncio.create_task(func2())


# Step #2
def on_connected(connection):
    """Called when we are fully connected to RabbitMQ"""
    # Open a channel
    connection.channel(on_open_callback=on_channel_open)

# Step #3
def on_channel_open(new_channel):
    """Called when our channel has opened"""
    global channel
    channel = new_channel
    channel.queue_declare(queue="test", durable=True, exclusive=False, auto_delete=False, callback=on_queue_declared)

# Step #4
def on_queue_declared(frame):
    """Called when RabbitMQ has told us our Queue has been declared, frame is the response from RabbitMQ"""
    channel.basic_consume('test', handle_delivery)


# Step #5
def handle_delivery(channel, method, header, body):
    """Called when we receive a message from RabbitMQ"""
    message = json.loads(body.decode())
    m = parse_obj_as(WebhookMatch, message)
    channel.basic_ack(delivery_tag=method.delivery_tag)


def consume():
    parameters = pika.ConnectionParameters()
    connection = pika.SelectConnection(parameters, on_open_callback=on_connected)

    try:
        # Loop so we can communicate with RabbitMQ
        connection.ioloop.start()
    except KeyboardInterrupt:
        # Gracefully close the connection
        connection.close()
        # Loop until we're fully closed, will stop on its own
        connection.ioloop.start()


def publish():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    # channel.queue_declare(queue='test')
    channel.basic_publish(exchange='',
                          routing_key='test',
                          body=b'Hello World!')
    print(" [x] Sent 'Hello World!'")


if __name__ == '__main__':
    consume()
    # publish()