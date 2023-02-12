import json

import pika
from pika import ConnectionParameters
from pika.channel import Channel
from pydantic import parse_obj_as

from application.web.models.events import WebhookMatch


class RabbitClient:
    # Step #1
    def __init__(self, host: str, port: int, user: str, password: str):
        """Instantiating RabbiMQ connection"""
        self.parameters: ConnectionParameters = ConnectionParameters(host=host, port=port, credentials=pika.PlainCredentials(user, password))
        self.connection = pika.SelectConnection(self.parameters, on_open_callback=self.on_connected)
        self.channel: Channel | None = None

    # Step #2
    def on_connected(self, connection):
        """Called when we are fully connected to RabbitMQ"""
        # Open a channel
        connection.channel(on_open_callback=self.on_channel_open)

    # Step #3
    def on_channel_open(self, new_channel):
        """Called when our channel has opened"""
        self.channel = new_channel
        self.channel.queue_declare(queue="matches", durable=True, exclusive=False, auto_delete=False,
                                   callback=self.on_queue_declared)

    # Step #4
    def on_queue_declared(self, frame):
        """Called when RabbitMQ has told us our Queue has been declared, frame is the response from RabbitMQ"""
        self.channel.basic_consume('matches', self.handle_delivery)

    # Step #5
    def handle_delivery(self, channel, method, header, body):
        """Called when we receive a message from RabbitMQ"""
        message = json.loads(body.decode())
        m = parse_obj_as(WebhookMatch, message)
        # discord bot logic
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def consume(self, ):
        try:
            # Loop so we can communicate with RabbitMQ
            self.connection.ioloop.start()
        except KeyboardInterrupt:
            # Gracefully close the connection
            self.connection.close()
            # Loop until we're fully closed, will stop on its own
            self.connection.ioloop.start()

    def publish(self, message: str, routing_key: str = "matches") -> None:
        connection = pika.BlockingConnection(self.parameters)
        channel = connection.channel()
        channel.queue_declare(queue=routing_key, durable=True, exclusive=False, auto_delete=False)
        channel.basic_publish(exchange='',
                              routing_key=routing_key,
                              body=message.encode())
