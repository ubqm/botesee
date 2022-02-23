import discord
import os
from IPython.terminal.pt_inputhooks.asyncio import loop
from flask import Flask, request, Response
from threading import Thread
from functools import partial
from discord_funcs import MyDiscordClient
from env_variables import discord_token


app = Flask(__name__)


@app.route("/", methods=["GET"])
def respond_default_get():
    return Response(status=200)


@app.route("/match_status_ready", methods=["POST"])
def respond_status_ready():
    print(request.json)
    loop.create_task(bot_client.post_faceit_message_ready(channel_id=828940900033626113, request_json=request.json))
    print("respond match_status_ready function called")
    return Response(status=200)


@app.route("/match_status_finished", methods=["POST"])
def respond_status_finished():
    print(request.json)
    loop.create_task(bot_client.post_faceit_message_finished(channel_id=828940900033626113, request_json=request.json))
    print("respond match_status_finished function called")
    return Response(status=200)


@app.route("/match_status_aborted", methods=["POST"])
def respond_status_aborted():
    print(request.json)
    loop.create_task(bot_client.post_faceit_message_aborted(channel_id=828940900033626113, request_json=request.json))
    print("respond match_status_aborted function called")
    return Response(status=200)


if __name__ == "__main__":
    intents = discord.Intents.all()
    bot_client = MyDiscordClient(intents=intents)

    port = int(os.environ.get("PORT", 5000))
    print(f"variable port:{port}")
    partial_run = partial(app.run, host="0.0.0.0", port=port)

    t = Thread(target=partial_run)
    t.start()

    bot_client.run(discord_token)
