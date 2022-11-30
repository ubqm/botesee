import asyncio

import discord
import os
import flask
from flask import Flask, request, Response
from threading import Thread
from functools import partial

from tortoise import run_async

from db.init import init
from discord_funcs import MyDiscordClient
from env_variables import discord_token
from database import db_fetch_data


async def main():
    app = Flask(__name__)

    @app.route("/", methods=["GET"])
    async def respond_default_get():
        player_data, matches_data, elo_data = await db_fetch_data()
        context = {"players": player_data, "matches": matches_data, "elo": elo_data}
        return flask.render_template('index.html', **context)

    @app.route("/match_status_ready", methods=["POST"])
    async def respond_status_ready():
        print(request.json)
        await bot_client.post_faceit_message_ready(
            channel_id=828940900033626113, request_json=request.json)
        print("respond match_status_ready function called")
        return Response(status=200)

    @app.route("/match_status_finished", methods=["POST"])
    async def respond_status_finished():
        print(request.json)
        await bot_client.post_faceit_message_finished(
            channel_id=828940900033626113, request_json=request.json)
        print("respond match_status_finished function called")
        return Response(status=200)

    @app.route("/match_status_aborted", methods=["POST"])
    async def respond_status_aborted():
        print(request.json)
        await bot_client.post_faceit_message_aborted(
            channel_id=828940900033626113, request_json=request.json)
        print("respond match_status_aborted function called")
        return Response(status=200)

    intents = discord.Intents.all()
    loop = asyncio.get_running_loop()
    bot_client = MyDiscordClient(intents=intents, loop=loop)

    port = int(os.environ.get("PORT", 5000))
    print(f"variable port:{port}")
    partial_run = partial(app.run, host="0.0.0.0", port=port)

    await init()
    t1 = Thread(target=partial_run, daemon=False)
    t1.start()

    await bot_client.start(discord_token)


if __name__ == "__main__":
    asyncio.run(main())
    # intents = discord.Intents.all()
    # bot_client = MyDiscordClient(intents=intents)
    #
    # port = int(os.environ.get("PORT", 5000))
    # print(f"variable port:{port}")
    # partial_run = partial(app.run, host="0.0.0.0", port=port)
    #
    # run_async(init())
    # t1 = Thread(target=partial_run, daemon=False)
    # t1.start()
    #
    # bot_client.run(discord_token)
